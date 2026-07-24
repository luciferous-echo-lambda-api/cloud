variable "system_name" {
  type     = string
  nullable = false
}

variable "region" {
  type     = string
  nullable = false
}

variable "slack_incoming_webhook_error_notifier_01" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "nocobase_domain" {
  type     = string
  nullable = false
}

variable "nocobase_collection" {
  type     = string
  nullable = false
}

variable "nocobase_api_key" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "cf_access_client_id" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "cf_access_client_secret" {
  type      = string
  nullable  = false
  sensitive = true
}
