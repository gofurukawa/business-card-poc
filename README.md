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

## 使い方

### サンプル名刺の生成

```bash
python src/generator.py templates/sample_card.json -o output/card.png
```

生成された名刺画像は `output/card.png` に保存されます。

### プレースホルダーの置換

テンプレート内の `{{KEY}}` 形式のプレースホルダーを置換して生成できます：

```bash
python src/generator.py templates/sample_card.json -o output/custom.png \
  --set NAME_KANJI="田中 太郎" \
  --set COMPANY_NAME="株式会社サンプル"
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
