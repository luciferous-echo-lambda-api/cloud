# Dependabotによるdocker-compose.ymlのイメージ管理

## 目的
イメージの追随を楽にしたい

## 要望
Dependabotでdocker-compose.ymlも管理可能なら管理してほしい

## 完了サマリー

- 完了日時: 2026-07-23T10:48:25+09:00
- `docker-compose.yml` の `floci` イメージタグを `latest` → `1.5.5` に固定（`latest` のままではDependabotがバージョン更新を検知できないため）。
- `.github/dependabot.yml` に `package-ecosystem: "docker-compose"`（`interval: weekly`）のエントリを追加。
- `make compose-up` / `make test-unit`（34件全PASS）/ `make compose-down` で動作確認済み。
- 詳細は `log.md` を参照。
