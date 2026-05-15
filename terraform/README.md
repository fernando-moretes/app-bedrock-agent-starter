# Terraform skeleton

Provisions the AWS surface needed to run the agent as a Lambda behind an HTTP API.

## What it creates

- Lambda function (Python 3.12) running `agent.handler.handler`.
- API Gateway HTTP API with a `POST /chat` route → Lambda integration.
- DynamoDB `sessions` table (pay-per-request, TTL enabled).
- IAM role with `bedrock:InvokeModel`, `bedrock:Converse*`, DynamoDB R/W on the sessions table, and CloudWatch logs.
- CloudWatch log group with 14-day retention.

## What is intentionally omitted

- Tags and naming conventions — adapt to your org.
- KMS keys (defaults to AWS-managed KMS).
- Custom domain on the HTTP API.
- WAF on the API.
- Remote Terraform state backend.

## Usage

Build the Lambda package first (see `../scripts/build_lambda.sh`), then:

```bash
terraform init
terraform apply \
  -var="project=my-agent" \
  -var="lambda_zip=../build/lambda.zip"
```

The output `api_url` is your POST endpoint:

```bash
curl -X POST "$(terraform output -raw api_url)/chat" \
  -H 'content-type: application/json' \
  -d '{"message": "what time is it?"}'
```
