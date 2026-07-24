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

# ================================================================
# Lambda URL Functions
# ================================================================

module "lambda_url_functions" {
  source = "../lambda_function"

  identifier  = "url_functions"
  handler     = "handlers/url_functions/url_functions.handler"
  role_arn    = aws_iam_role.lambda_url_functions.arn
  timeout     = 60
  memory_size = 512

  environment_variables = {
    DDB_TABLE_NAME = aws_dynamodb_table.tmp.name
  }

  subscription_destination_lambda_arn = module.lambda_error_processor.function_alias_arn

  s3_bucket_deploy_package = aws_s3_object.lambda_deploy_package.bucket
  s3_key_deploy_package    = aws_s3_object.lambda_deploy_package.key
  source_code_hash         = data.archive_file.lambda_deploy_package.output_base64sha256
  system_name              = var.system_name
  region                   = var.region
}

resource "aws_lambda_function_url" "url_functions" {
  authorization_type = "NONE"
  function_name      = module.lambda_url_functions.function_name
  qualifier          = module.lambda_url_functions.function_alias_name
}

resource "aws_lambda_permission" "url_functions_url" {
  statement_id  = "FunctionUrlAllowPublicAccessForUrl"
  action        = "lambda:InvokeFunctionUrl"
  function_name = module.lambda_url_functions.function_name
  qualifier     = module.lambda_url_functions.function_alias_name
  principal     = "*"

  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "url_functions_invoke" {
  statement_id  = "FunctionUrlAllowPublicAccessForInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_url_functions.function_name
  qualifier     = module.lambda_url_functions.function_alias_name
  principal     = "*"
}

# ================================================================
# Lambda NocoBase Inserter
# ================================================================

module "lambda_nocobase_inserter" {
  source = "../lambda_function"

  identifier  = "nocobase_inserter"
  handler     = "handlers/nocobase_inserter/nocobase_inserter.handler"
  role_arn    = aws_iam_role.lambda_nocobase_inserter.arn
  timeout     = 60
  memory_size = 512

  environment_variables = {
    SSM_PARAMETER_NAME_NOCOBASE_DOMAIN         = aws_ssm_parameter.nocobase_domain.name
    SSM_PARAMETER_NAME_NOCOBASE_COLLECTION     = aws_ssm_parameter.nocobase_collection.name
    SSM_PARAMETER_NAME_NOCOBASE_API_KEY        = aws_ssm_parameter.nocobase_api_key.name
    SSM_PARAMETER_NAME_CF_ACCESS_CLIENT_ID     = aws_ssm_parameter.cf_access_client_id.name
    SSM_PARAMETER_NAME_CF_ACCESS_CLIENT_SECRET = aws_ssm_parameter.cf_access_client_secret.name
    DDB_TABLE_NAME                             = aws_dynamodb_table.tmp.name
  }

  subscription_destination_lambda_arn = module.lambda_error_processor.function_alias_arn

  s3_bucket_deploy_package = aws_s3_object.lambda_deploy_package.bucket
  s3_key_deploy_package    = aws_s3_object.lambda_deploy_package.key
  source_code_hash         = data.archive_file.lambda_deploy_package.output_base64sha256
  system_name              = var.system_name
  region                   = var.region
}

resource "aws_lambda_event_source_mapping" "nocobase_inserter" {
  function_name     = module.lambda_nocobase_inserter.function_alias_arn
  event_source_arn  = aws_dynamodb_table.tmp.stream_arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
  enabled           = true
}
