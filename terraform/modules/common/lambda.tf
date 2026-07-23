# ================================================================
# Lambda Deploy Package
# ================================================================

data "archive_file" "lambda_deploy_package" {
  type        = "zip"
  output_path = "lambda_deploy_package.zip"
  source_dir  = "${path.root}/../../../src"
}

resource "aws_s3_object" "lambda_deploy_package" {
  bucket        = aws_s3_bucket.lambda_artifacts.bucket
  key           = "lambda_deploy_package.zip"
  source        = data.archive_file.lambda_deploy_package.output_path
  etag          = data.archive_file.lambda_deploy_package.output_md5
  storage_class = "STANDARD_IA"
}

# ================================================================
# Lambda Error Processor
# ================================================================

module "lambda_error_processor" {
  source = "../lambda_function_basic"

  identifier = "error_processor"
  handler    = "handlers/error_processor/error_processor.handler"
  role_arn   = aws_iam_role.lambda_error_processor.arn
  layers     = ["arn:aws:lambda:${var.region}:043309354008:layer:LuciferousPublicLayerAwsCloudwatchLogsUrlPython314:1"]

  environment_variables = {
    SYSTEM_NAME    = var.system_name
    EVENT_BUS_NAME = aws_cloudwatch_event_bus.slack_error_notifier.name
  }

  s3_bucket_deploy_package = aws_s3_object.lambda_deploy_package.bucket
  s3_key_deploy_package    = aws_s3_object.lambda_deploy_package.key
  source_code_hash         = data.archive_file.lambda_deploy_package.output_base64sha256
  system_name              = var.system_name
  region                   = var.region
}

resource "aws_lambda_permission" "error_processor" {
  for_each = {
    Function = module.lambda_error_processor.function_arn
    Alias    = module.lambda_error_processor.function_alias_arn
  }

  statement_id   = "AllowLogsInvoke${each.key}"
  action         = "lambda:InvokeFunction"
  function_name  = each.value
  principal      = "logs.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
}
