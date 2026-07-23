resource "aws_lambda_function" "function" {
  function_name                  = replace("${var.system_name}-${var.identifier}", "_", "-")
  role                           = var.role_arn
  runtime                        = "python3.14"
  architectures                  = ["arm64"]
  handler                        = var.handler
  memory_size                    = var.memory_size
  timeout                        = var.timeout
  s3_bucket                      = var.s3_bucket_deploy_package
  s3_key                         = var.s3_key_deploy_package
  source_code_hash               = var.source_code_hash
  reserved_concurrent_executions = var.reserved_concurrent_executions
  publish                        = true

  dynamic "snap_start" {
    for_each = var.enable_snap_start ? [1] : []
    content {
      apply_on = "PublishedVersions"
    }
  }

  layers = concat(var.layers, [
    "arn:aws:lambda:${var.region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python314-arm64:33"
  ])

  environment {
    variables = merge(
      {
        POWERTOOLS_SERVICE_NAME = var.powertools_service_name != null && var.powertools_service_name != "" ? var.powertools_service_name : var.identifier
      },
      var.environment_variables
    )
  }
}

resource "aws_lambda_alias" "function" {
  function_name    = aws_lambda_function.function.function_name
  function_version = aws_lambda_function.function.version
  name             = var.alias
}
