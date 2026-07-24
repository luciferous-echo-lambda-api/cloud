resource "random_uuid4" "ddb_tmp" {}

resource "aws_dynamodb_table" "tmp" {
  name             = "tmp-${random_uuid4.ddb_tmp.result}"
  hash_key         = "id"
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "KEYS_ONLY"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}