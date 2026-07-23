# ================================================================
# Config
# ================================================================

terraform {
  required_version = "~> 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.42"
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

# ================================================================
# Outputs
# ================================================================

output "ssm_parameter_prefix_outputs" {
  value = module.common.ssm_parameter_prefix_outputs
}