#!/bin/bash
for i in {1..20}
do
  ab -n 10 -c 1 -H "X-Forwarded-For: 1.2.3.4" http://your-server-endpoint/
  sleep 3
done

# chmod +x test2.sh
# ./test2.sh
