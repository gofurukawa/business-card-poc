# Business Card Generator PoC

JSON レイアウト定義から日本語対応の名刺画像（PNG）を生成する PoC プロジェクトです。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. フォントのダウンロード

以下のサイトから日本語フォントをダウンロードし、`fonts/` ディレクトリに配置してください：

- **Noto Sans JP（ゴシック体）**: https://fonts.google.com/noto/specimen/Noto+Sans+JP
- **Noto Serif JP（明朝体）**: https://fonts.google.com/noto/specimen/Noto+Serif+JP

各サイトで「Download family」ボタンをクリックしてZIPファイルをダウンロードし、解凍後のttfファイルを `fonts/` ディレクトリに配置します。

必要なフォントファイル：
- `NotoSansJP-Regular.ttf`
- `NotoSansJP-Bold.ttf`
- `NotoSansJP-Light.ttf`
- `NotoSerifJP-Regular.ttf`
- `NotoSerifJP-Bold.ttf`
- `NotoSerifJP-Light.ttf`

## テンプレート

2種類のサンプルテンプレートを用意しています：

| ファイル | 説明 |
|----------|------|
| `templates/sample_card.json` | デフォルト値入り（そのまま生成可能） |
| `templates/sample_card_template.json` | プレースホルダー形式（値の指定が必要） |

## 使い方

### サンプル名刺の生成

```bash
python src/generator.py templates/sample_card.json -o output/card.png
```

生成された名刺画像は `output/card.png` に保存されます。

### プレースホルダーの置換

`sample_card_template.json` は `{{KEY}}` 形式のプレースホルダーを使用しています。`--set` オプションで値を指定して生成できます：

```bash
python src/generator.py templates/sample_card_template.json -o output/custom.png \
  --set COMPANY_NAME="株式会社サンプル" \
  --set DEPARTMENT="営業部" \
  --set NAME_KANJI="田中 太郎" \
  --set NAME_ROMAJI="Taro Tanaka" \
  --set TITLE="部長" \
  --set POSTAL_CODE="100-0001" \
  --set ADDRESS="東京都千代田区丸の内1-1-1" \
  --set PHONE="03-1234-5678" \
  --set EMAIL="t.tanaka@example.co.jp"
```

### カスタムフォントパスの指定

```bash
python src/generator.py templates/sample_card.json -o output/card.png \
  --font-path /path/to/custom/fonts/
```

## 技術仕様

- 名刺サイズ: 91mm × 55mm（日本標準サイズ）
- 解像度: 300 DPI（印刷品質）
- 出力形式: PNG
