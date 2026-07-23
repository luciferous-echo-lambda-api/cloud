variable "function_name" {
  description = "Lambda function name"
  type        = string
  nullable    = false
}

variable "alias_name" {
  description = "Lambda alias name"
  type        = string
  nullable    = false
}

variable "region" {
  description = "AWS region"
  type        = string
  nullable    = false
}

variable "lambda_version" {
  description = "Lambda function version to trigger cleanup. Since the Alias always points to the latest version, this variable effectively triggers cleanup to keep only the latest version."
  type        = string
  nullable    = false
}
