# ================================================================
# Config
# ================================================================

terraform {
  required_version = "~> 1.15"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.56"
    }
  }

  backend "s3" {
    bucket = null
    key    = null
    region = null
  }
}

# ================================================================
# Provider
# ================================================================

provider "aws" {
  region = var.REGION

  default_tags {
    tags = {
      SystemName = var.SYSTEM_NAME
    }
  }
}

# ================================================================
# Modules
# ================================================================

module "common" {
  source = "../../modules/common"

  system_name = var.SYSTEM_NAME
  region      = var.REGION

  cf_access_client_id     = var.CF_ACCESS_CLIENT_ID
  cf_access_client_secret = var.CF_ACCESS_CLIENT_SECRET
  nocobase_api_key        = var.NOCOBASE_API_KEY
  nocobase_collection     = var.NOCOBASE_COLLECTION
  nocobase_domain         = var.NOCOBASE_DOMAIN

  slack_incoming_webhook_error_notifier_01 = var.SLACK_INCOMING_WEBHOOK_ERROR_NOTIFIER_01
}

# ================================================================
# Variables
# ================================================================

variable "SYSTEM_NAME" {
  type     = string
  nullable = false
}

variable "REGION" {
  type     = string
  nullable = false
}

variable "SLACK_INCOMING_WEBHOOK_ERROR_NOTIFIER_01" {
  type     = string
  nullable = false
}

variable "CF_ACCESS_CLIENT_ID" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "CF_ACCESS_CLIENT_SECRET" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "NOCOBASE_API_KEY" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "NOCOBASE_COLLECTION" {
  type     = string
  nullable = false
}

variable "NOCOBASE_DOMAIN" {
  type     = string
  nullable = false
}

# ================================================================
# Outputs
# ================================================================

output "ssm_parameter_prefix_outputs" {
  value = module.common.ssm_parameter_prefix_outputs
}