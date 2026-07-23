# Dependabot設定

## 目的
依存ライブラリやGithub Actionsなどに対してバージョンアップなどを自動で提案してほしい。

## 要望
dependabotの設定をして欲しい。なおboto3, botocore, boto3-stubs, aws-lambda-powertoolsについては除外して欲しい。

## 完了サマリー

- 完了日時: 2026-07-23T10:40:20+09:00
- `.github/dependabot.yml` を新規作成した。
  - `package-ecosystem: "uv"`（`pyproject.toml` の依存を対象）、`ignore` で `boto3` / `botocore` / `boto3-stubs` / `aws-lambda-powertools` を除外し、週次スケジュールを設定。
  - `package-ecosystem: "github-actions"`（`.github/workflows/*.yml` を対象）、週次スケジュールを設定。
- `uv run --with pyyaml` を使い YAML 構文の妥当性を検証済み。
- プライベート PyPI インデックス（`pypi.flatt.tech`）へのアクセスに認証設定が必要になる可能性がある点は既知の注意点として残した（本タスクのスコープ外）。
- 詳細は `kanban/0001_setup_dependabot/log.md` を参照。
