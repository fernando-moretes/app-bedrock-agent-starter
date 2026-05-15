output "api_url" {
  value       = aws_apigatewayv2_api.http.api_endpoint
  description = "Base URL of the HTTP API. POST /chat is the only route."
}

output "lambda_name" {
  value = aws_lambda_function.agent.function_name
}

output "sessions_table" {
  value = aws_dynamodb_table.sessions.name
}
