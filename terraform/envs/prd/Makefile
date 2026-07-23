SHELL = /usr/bin/env bash -xeuo pipefail

init:
	@terraform init \
		-backend-config="bucket=$$BACKEND_S3_BUCKET" \
		-backend-config="key=$$BACKEND_S3_KEY" \
		-backend-config="region=$$BACKEND_REGION"

plan:
	@terraform plan

apply:
	@terraform apply -auto-approve

get-outputs:
	@prefix=$$(terraform output -raw ssm_parameter_prefix_outputs) && \
	aws ssm get-parameters-by-path \
		--path "$$prefix" \
		--with-decryption \
		--query "Parameters[*].{Name:Name,Value:Value}" \
		--output json


.PHONY: \
	init \
	plan \
	apply \
	get-outputs
