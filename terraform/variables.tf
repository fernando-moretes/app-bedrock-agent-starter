variable "project" {
  type        = string
  description = "Project name used as resource prefix."
}

variable "region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region. Bedrock model availability varies by region."
}

variable "lambda_zip" {
  type        = string
  description = "Path to the zipped Lambda deployment package."
}

variable "model_id" {
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
  description = "Bedrock model id used by the agent."
}

variable "max_tool_rounds" {
  type        = number
  default     = 8
  description = "Cap on tool-call rounds per turn — defense against loops."
}
