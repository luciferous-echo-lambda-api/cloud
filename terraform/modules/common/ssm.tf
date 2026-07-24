locals {
  ssm = {
    prefix_outputs = "/${var.system_name}/outputs"
    prefix_secrets = "/${var.system_name}/secrets"
  }
}

# ================================================================
# Secrets
# ================================================================

resource "aws_ssm_parameter" "nocobase_domain" {
  name  = "${local.ssm.prefix_secrets}/nocobase_domain"
  type  = "String"
  value = var.nocobase_domain
}

resource "aws_ssm_parameter" "nocobase_collection" {
  name  = "${local.ssm.prefix_secrets}/nocobase_collection"
  type  = "String"
  value = var.nocobase_collection
}

resource "aws_ssm_parameter" "nocobase_api_key" {
  name  = "${local.ssm.prefix_secrets}/nocobase_api_key"
  type  = "SecureString"
  value = var.nocobase_api_key
}

resource "aws_ssm_parameter" "cf_access_client_id" {
  name  = "${local.ssm.prefix_secrets}/cf_access_client_id"
  type  = "SecureString"
  value = var.cf_access_client_id
}

resource "aws_ssm_parameter" "cf_access_client_secret" {
  name  = "${local.ssm.prefix_secrets}/cf_access_client_secret"
  type  = "SecureString"
  value = var.cf_access_client_secret
}
