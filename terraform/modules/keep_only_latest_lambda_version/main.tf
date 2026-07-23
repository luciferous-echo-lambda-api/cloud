resource "null_resource" "delete_unused_versions" {
  triggers = {
    function_name  = var.function_name
    alias_name     = var.alias_name
    lambda_version = var.lambda_version
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -e

      # This module keeps only the version that the Alias points to (which is always the latest version)
      # and deletes all other versions to reduce Lambda Snap Start costs.
      # The Alias is expected to always point to the latest deployed version.

      FUNCTION_NAME="${var.function_name}"
      ALIAS_NAME="${var.alias_name}"
      REGION="${var.region}"

      echo "Getting alias version for function $FUNCTION_NAME with alias $ALIAS_NAME..."
      ALIAS_VERSION=$(aws lambda get-alias \
        --function-name "$FUNCTION_NAME" \
        --name "$ALIAS_NAME" \
        --region "$REGION" \
        --query 'FunctionVersion' \
        --output text 2>/dev/null || echo "")

      if [ -z "$ALIAS_VERSION" ]; then
        echo "Failed to get alias version. Skipping cleanup."
        exit 0
      fi

      echo "Alias version: $ALIAS_VERSION"

      echo "Getting all versions..."
      ALL_VERSIONS=$(aws lambda list-versions-by-function \
        --function-name "$FUNCTION_NAME" \
        --region "$REGION" \
        --query 'Versions[?Version!=`$LATEST`].Version' \
        --output text)

      echo "All versions: $ALL_VERSIONS"
      echo "Deleting versions except $ALIAS_VERSION..."

      for version in $ALL_VERSIONS; do
        if [ "$version" != "$ALIAS_VERSION" ]; then
          echo "Deleting version $version..."
          aws lambda delete-function \
            --function-name "$FUNCTION_NAME" \
            --qualifier "$version" \
            --region "$REGION" || echo "Failed to delete version $version (may have been deleted already)"
        fi
      done

      echo "Cleanup complete. Kept version: $ALIAS_VERSION"
    EOT
  }
}
