SHELL = /usr/bin/env bash -xeuo pipefail

fmt-python:
	uv run isort src/ tests/
	uv run black src/ tests/

fmt-tf-envs-prd:
	cd terraform/envs/prd; \
	terraform fmt

fmt-tf-modules-common:
	cd terraform/modules/common; \
	terraform fmt

fmt-tf-modules-events-slack-webhook-destination:
	cd terraform/modules/events_slack_webhook_destination; \
	terraform fmt

fmt-tf-modules-keep-only-latest-lambda-version:
	cd terraform/modules/keep_only_latest_lambda_version; \
	terraform fmt

fmt-tf-modules-lambda-function:
	cd terraform/modules/lambda_function; \
	terraform fmt

fmt-tf-modules-lambda-function-basic:
	cd terraform/modules/lambda_function_basic; \
	terraform fmt

fmt-terraform: \
	fmt-tf-envs-prd \
	fmt-tf-modules-common \
	fmt-tf-modules-events-slack-webhook-destination \
	fmt-tf-modules-keep-only-latest-lambda-version \
	fmt-tf-modules-lambda-function \
	fmt-tf-modules-lambda-function-basic

format: \
	fmt-terraform \
	fmt-python

compose-up:
	docker compose up -d

compose-down:
	docker compose down

test-unit:
	uv run pytest -vv tests/unit

.PHONY: \
	fmt-python \
	fmt-tf-envs-prd \
	fmt-tf-modules-common \
	fmt-tf-modules-events-slack-webhook-destination \
	fmt-tf-modules-keep-only-latest-lambda-version \
	fmt-tf-modules-lambda-function \
	fmt-tf-modules-lambda-function-basic \
	fmt-terraform \
	format \
	compose-up \
	compose-down \
	test-unit
