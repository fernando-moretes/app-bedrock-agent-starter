# Deployment

The Terraform skeleton provisions the minimum AWS surface for a serverless agent API:

- AWS Lambda running the Python handler.
- API Gateway HTTP API with `POST /chat`.
- DynamoDB table for session memory.
- CloudWatch log group.
- IAM role and policy for Bedrock, DynamoDB, and basic Lambda logging.

## Build the Lambda package

```bash
bash scripts/build_lambda.sh
```

## Apply Terraform

```bash
cd terraform
terraform init
terraform apply \
  -var="project=bedrock-agent-starter" \
  -var="lambda_zip=../dist/lambda.zip"
```

## Production notes

- Add remote state before team usage.
- Scope Bedrock model permissions to approved models where possible.
- Add account-level tagging and IAM boundaries according to your organization standards.
- Put API Gateway behind auth before exposing it publicly.
- Consider Bedrock Guardrails for external-facing agents.
