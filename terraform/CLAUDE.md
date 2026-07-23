# CLAUDE.md (terraform/)

### Terraform モジュール階層

```
envs/prd → modules/common → modules/lambda_function_basic
                          → modules/events_slack_webhook_destination
```

- `envs/prd`: ルートモジュール。S3 backend（bucket/key/region は `make init` の env 経由で注入）。`module "common"` のみを呼ぶ。
- `modules/common`: 実際にデプロイされるインフラ本体。error_processor Lambda・S3 アーティファクトバケット・EventBridge バス + Slack API destination・IAM・自己監視用の SNS + CloudWatch アラームをまとめる。
- `modules/lambda_function_basic`: Lambda 関数 + alias + ロググループの基底モジュール。runtime `python3.14` / arm64 / 常に `publish = true`、Powertools レイヤを自動付与、SnapStart は任意。
- `modules/events_slack_webhook_destination`: EventBridge ルール + API destination + `input_transformer` による Slack 連携。

**未接続のテンプレートモジュール**（現状どの env からも呼ばれていない。消費側 Lambda を追加する際の雛形）:

- `modules/lambda_function`: `lambda_function_basic` をラップし、`aws_cloudwatch_log_subscription_filter`（`{ $.level = "ERROR" }` および `"Task timed out"` 等の異常終了パターン）を追加する。**error_processor に自分のエラーログを流したい消費側 Lambda はこのモジュールを使う。** error_processor 自体は `lambda_function_basic` 直接なので、この購読経路はまだ配線されていない。
- `modules/keep_only_latest_lambda_version`: `null_resource` + `local-exec` で alias が指す最新版以外の Lambda バージョンを削除（SnapStart コスト削減用）。
