# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

LambdaによるAPIバックエンド処理において、リクエストの内容をそのまま返すAPIを作成する。
また、リクエストの内容はNocoBaseにも送信し記録する。

## コマンド

すべて Makefile 経由。Python は `uv` で管理する。

- **ユニットテスト**: `make test-unit` (= `uv run pytest -vv tests/unit`)
  - **事前に `make compose-up` が必須**。EventBridge の結合テストは `docker-compose.yml` の `floci`（LocalStack 互換, `localhost:4566`）に接続するため、起動していないと失敗する。終了は `make compose-down`。
  - 単体実行例: `uv run pytest -vv tests/unit/handlers/error_processor/test_error_processor.py::TestParseLogMessage::test_normal`
- **フォーマット**: `make format`（Python の isort/black と全 Terraform モジュールの `terraform fmt`）。Python のみは `make fmt-python`。
- **依存解決**: `uv sync --all-groups --all-extras`。
- **デプロイ**: `v*` タグを push すると `release-prd.yml` → `deploy.yml` が走り prd 環境へ `terraform apply`（`workflow_dispatch` でも手動起動可）。ローカルからは `terraform/envs/prd/Makefile` の `init` / `plan` / `apply` を使う（`.envrc` にバックエンド設定が必要、`.envrc.example` 参照）。

### 注意

- **プライベート PyPI**: `pyproject.toml` は `https://pypi.flatt.tech/simple/` を **default index** に設定している。`uv sync` はパブリック PyPI では解決しない。
- `.github/workflows/test_unit.yml` の `on.push.branches` は空でありプレースホルダー。CI は現状 push で自動起動しない。

## アーキテクチャ

### 実行時のデータフロー（error_processor）

`src/handlers/error_processor/error_processor.py` が唯一デプロイされる Lambda。

1. CloudWatch Logs のサブスクリプションフィルタから gzip+base64 の `CloudWatchLogsEvent` を受信（`@event_source` でデコード）。
2. 各ログイベントを `parse_message` で `LogMessage` に変換。Powertools 形式の JSON（`stack_trace` 等）をパースし、失敗時は素のメッセージにフォールバック。
3. `create_slack_payload` で Lambda コンソール・CloudWatch Logs へのリンク付き Slack Block Kit ペイロードを組み立てる。
4. `put_events` で EventBridge バス `error_notifier` に投入。**10 件ずつバッチ**投入し、失敗分は成功集合と全体集合が一致するまでリトライする。
5. （インフラ側）EventBridge ルールが account 一致で発火 → API destination 経由で Slack Incoming Webhook へ。`input_transformer` が `$.detail.blocks` を Slack ペイロードに整形する。

### ロガー抽象化（`src/utils/logger/`）

AWS Lambda Powertools Logger を薄くラップした `Logger`（`create_logger(__name__)` で生成）。コード全体はこの 2 つのデコレータで統一されている:

- `@logging_handler(logger)`: Lambda ハンドラをラップ。Powertools の lambda context を注入し、イベントと環境変数（`EXCLUDE_ENV_KEYS` の秘匿値は除外）をログ出力、戻り値・例外も記録。
- `@logging_function(logger)`: 任意の関数をラップ。UUID7 の CallID を採番し、開始・終了・引数・戻り値・実行時間・例外を DEBUG ログに残す。

`logger.py` の `custom_default` は Powertools への JSON シリアライザで、tuple/set・datetime・bytes（gzip 圧縮 + base64）・Decimal・Powertools の `DictWrapper`・pydantic `BaseModel`・dataclass を扱う。新しい非標準型をログに乗せる場合はここを拡張する。

### AWS クライアントファクトリ（`src/utils/aws/aws.py`）

`create_client` / `create_resource` は `@functools.lru_cache` でキャッシュし、既定 botocore config（connect/read timeout 5s、standard retries）を適用する。`main()` は `client_events: EventBridgeClient = create_client("events")` を **デフォルト引数**で受け取り、テスト時に LocalStack 向けクライアントを注入できる（DI パターン）。resource はスレッドセーフでない点に注意（コメント記載）。

環境変数は `pydantic_settings.BaseSettings`（`EnvironmentVariables`）で読む。

### Terraform モジュール階層

`terraform/` 配下の詳細（モジュール依存関係、未接続のテンプレートモジュール等）は `terraform/CLAUDE.md` を参照。

### デプロイパッケージング

`modules/common/lambda.tf` の `archive_file` が `src/` ディレクトリを zip 化 → S3 にアップロード → Lambda が S3 から読む。ハンドラパスは `handlers/error_processor/error_processor.handler`。pytest は `pythonpath = ["src"]`（`pyproject.toml`）なので、テスト・本番とも `import handlers...` / `import utils...` が `src/` 起点で解決される。
