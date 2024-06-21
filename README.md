# AWS WAF IP blocking Permenently from Rate Based Rule.
## Firstly we need to create WAF Web ACL: (Here I am going to create it for the Application load balancer.)
- Resource Type: Regional Resources.
- Region: Choose region of ALB.
- Name: xxxxx
- Add AWS Resources -> ALB -> Select your ALb -> Add.
## At this point you'll have Rules Option:
- It is required as we need to create Rate Based Rule that block IP If exceed Rate Limit.
 > Limitation of this Rule is that is Block ip for Few minutes only then it realese again.
- Add rules -> Add my own rules and rule groups ->
  - Rule type: Rule builder
  - Type: Rate-based rule
  - Rate limit: 100
  - Evaluation window: 1 minute (60 seconds)
  - Request aggregation: Source IP address
  - Scope of inspection and rate limiting: Consider all requests
  - Action: Block
- Then just Next, Next, Next.
## Now we will use cloudformation template to Create Following Resorurces:
- IPv4 Sets
- Lambda Function with code that add Blocked IP addresses to the IPv4Sets
- EventBridge Rule that trigger lambda function at every minute, so that it will check for the Updated RBR IP lists
- In Cloudformation template you need to add the following data:
  - Scope: REGIONAL
  - WebACLName: xxxxx
  - WebACLId: xxxxxx
  - RateBasedRuleName: xxxxx
- Then Create resources using CloudFormation.
## After Creating this We need change few things.
- Go to our Web ACL rule -> Add new Rule -> Add my own ->
  - Rule type: IP Set.
  - Rule name : x
  - IP set: Select IPSet create by Cloudformation.
  - IP address to use as the originating address: Source IP address.
  - Action: Block
- Add rule.
- make it prority top.
> Advance: If there are some ip you want to allow at any cost then create `IPset` that contain ip list of that IPs and then create rule with this IPset anf make it priority on the top. This will allow these ips to make request without getting blocked.
## all set now. Cloudfromation template and Code can be found in repo.

# Problem of this solution and solution to it.
## For now we are thinking it like a tester not ddos attacker.
- The script which we are running for test is very simple and our servers IP is sending directly and blockig it.
- **What actully attackers do?**: They don't want to reveal their IPs so they don't attack like we did. They use `HTTP Proxies` so source ip will always be changing. No fix IP to block, so our this set up won't work here. cause blocked IPset has limitation plus nothing is blocked here anyway, request still keep coming from different locations.
## `X-Forwarded-For` HTTP header:
- `X-Forwarded-For` http header used by proxy servers and load balancer, which tells originating IP. It indicates that request is forwarded from which IP.
- So, We are making changes in our rules.
## Rate Based Rule changes: 
- Request aggregation: IP address in header
- Header field name: `X-Forwarded-For`
- Fallback for missing IP address: Match
## IP set blocking rule:
- IP address to use as the originating address: IP address in header
- Keep all default.
## What's logic behind it??
- Now rate based limit rule will check `IP address in header` for the request that is coming instead of `source IP address`.
- Add that IP to the block list ( as our lambda function support both blocking ).
- IPset blocking rule is also block ip `IP address in header`, so when request comes, it matches the `IP from IP set`.
- So now any request will come then it will check `X-Forwarded-For` ip address and block request on that basis.
## How should I test this?
- Using ApacheBench.
- Ubuntu/Debian:
  ```sudo apt-get install apache2-utils```
- CentOS/RHEL:
  ```sudo yum install httpd-tools```
- Amazon Linux:
  ```sudo yum install httpd24-tools```
- Script `test.sh`:
  ```
  #!/bin/bash
  for i in {1..20}
  do
    ab -n 10 -c 1 -H "X-Forwarded-For: 1.2.3.4" http://your-server-endpoint/
    sleep 3
  done
  ```
- Make script executable:
  ```chmod +x test.sh```
- Run Script:
  ```./test.sh```
- Explanation: The script sends 10 requests (-n 10) every 3 seconds (sleep 3), totaling 200 requests over 60 seconds.
- Each request includes the X-Forwarded-For header with the value `1.2.3.4`.
