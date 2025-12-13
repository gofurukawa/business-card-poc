# Business Card Generator PoC

## 概要
JSON レイアウト定義から日本語対応の名刺画像（PNG）を生成する PoC プロジェクトです。

## 技術スタック
- Python 3.10+
- Pillow (PIL Fork) - 画像生成
- 日本語フォント: Noto Sans JP (ゴシック) / Noto Serif JP (明朝)

## ディレクトリ構成
```
business-card-poc/
├── CLAUDE.md              # このファイル
├── skills/
│   ├── card-analyzer/     # 名刺解析スキル（Step 2 で実装予定）
│   └── card-generator/    # 名刺生成スキル（Step 2 で実装予定）
├── src/
│   └── generator.py       # 名刺画像生成エンジン
├── schemas/
│   └── card_layout.schema.json  # レイアウト JSON スキーマ
├── templates/
│   └── sample_card.json   # サンプル名刺テンプレート
├── fonts/                 # フォントファイル格納ディレクトリ
├── input/                 # スキャン画像入力用（Step 2 以降）
└── output/                # 生成画像出力先
```

## スキル
- `skills/card-analyzer/SKILL.md` - 名刺画像の OCR・解析（未実装）
- `skills/card-generator/SKILL.md` - 名刺画像の生成ワークフロー（未実装）

## 開発時の注意点
- フォントパスは設定可能（デフォルト: `fonts/`、CLI引数 `--font-path` で変更可）
- 名刺サイズ: 91mm × 55mm（日本標準サイズ）
- 解像度: 300 DPI（印刷品質）
- JSON ファイルは UTF-8 エンコーディング必須
- プレースホルダー形式: `{{PLACEHOLDER_NAME}}`
- フォントが見つからない場合はエラーで停止

## よく使うコマンド

```bash
# 依存関係インストール
pip install -r requirements.txt

# 基本的な使い方
python src/generator.py templates/sample_card.json -o output/card.png

# プレースホルダーを置換して生成
python src/generator.py templates/sample_card.json -o output/tanaka.png \
  --set NAME_KANJI="田中 太郎" \
  --set COMPANY_NAME="株式会社サンプル"

# カスタムフォントパスを指定
python src/generator.py templates/sample_card.json -o output/card.png \
  --font-path /usr/share/fonts/noto-cjk/
```
