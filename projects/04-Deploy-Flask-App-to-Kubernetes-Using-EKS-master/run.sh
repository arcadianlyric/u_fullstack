export JWT_SECRET='myjwtsecret'
export LOG_LEVEL=DEBUG

python main.py

# docker
export TOKEN=`curl -d '{"email":"cc@gmail.com","password":"abc123"}' -H "Content-Type: application/json" -X POST localhost:8080/auth  | jq -r '.token'`
# echo $TOKEN
curl --request GET 'http://127.0.0.1:8080/contents' -H "Authorization: Bearer ${TOKEN}" | jq .

docker build -t "jwt-api-test" .
docker run --rm --env-file=.env_file -p 8080:8080 jwt-api-test

# create role
aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document file://trust.json --output text --query 'Role.Arn'
aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file://iam-role-policy.json

# create eks
eksctl create cluster --name eks-test
