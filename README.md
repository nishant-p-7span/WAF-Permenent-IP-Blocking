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
  > Advance: If there is any IPset rule which you are allowing then please make sure it always stays above this rule.
## all set now. Cloudfromation template and Code can be found in repo.
