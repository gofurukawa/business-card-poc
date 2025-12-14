# Card Generator Skill

名刺レイアウト JSON から PNG 画像を生成するスキルです。

## 概要

`src/generator.py` を使用して、JSON 形式のレイアウト定義から高品質な名刺画像を生成します。

## 基本コマンド

```bash
python src/generator.py <テンプレートファイル> -o <出力ファイル> [オプション]
```

## コマンド例

### サンプル名刺をそのまま生成

```bash
python src/generator.py templates/sample_card.json -o output/card.png
```

### プレースホルダーを置換して生成

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

### カスタムフォントパスを指定

```bash
python src/generator.py templates/sample_card.json -o output/card.png \
  --font-path /path/to/fonts/
```

### 解像度を変更（デフォルト: 300 DPI）

```bash
python src/generator.py templates/sample_card.json -o output/card.png --dpi 150
```

### 背景画像を使用して生成

```bash
python src/generator.py templates/sample_card_with_background.json -o output/card.png \
  --set BACKGROUND_IMAGE="../assets/card_background.png" \
  --set NAME_KANJI="田中 太郎" \
  --set DEPARTMENT="営業部"
```

## CLI オプション一覧

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `<template>` | JSON テンプレートファイルパス | （必須） |
| `-o, --output` | 出力 PNG ファイルパス | `output/card.png` |
| `--set KEY="value"` | プレースホルダー置換（複数指定可） | - |
| `--font-path` | フォントディレクトリパス | `fonts/` |
| `--dpi` | 出力解像度 | `300` |

## プレースホルダー一覧

`sample_card_template.json` で使用可能なプレースホルダー：

| プレースホルダー | 説明 | 例 |
|-----------------|------|-----|
| `{{COMPANY_NAME}}` | 会社名 | 株式会社テクノソリューションズ |
| `{{DEPARTMENT}}` | 部署名 | 技術開発本部 |
| `{{NAME_KANJI}}` | 氏名（漢字） | 山田 花子 |
| `{{NAME_ROMAJI}}` | 氏名（ローマ字） | Hanako Yamada |
| `{{TITLE}}` | 役職 | シニアエンジニア |
| `{{POSTAL_CODE}}` | 郵便番号 | 100-0005 |
| `{{ADDRESS}}` | 住所 | 東京都千代田区丸の内1-1-1 |
| `{{PHONE}}` | 電話番号 | 03-1234-5678 |
| `{{EMAIL}}` | メールアドレス | h.yamada@example.co.jp |

## フォントカテゴリマッピング

| カテゴリ | フォント | 用途 |
|---------|---------|------|
| `gothic` | Noto Sans JP | ゴシック体。会社名、部署、連絡先など |
| `mincho` | Noto Serif JP | 明朝体。氏名など格式ある表現 |

### フォントウェイト

| ウェイト | 説明 |
|---------|------|
| `light` | 細字。補助的な情報 |
| `regular` | 標準。一般的なテキスト |
| `bold` | 太字。氏名など強調したい要素 |

### 必要なフォントファイル

`fonts/` ディレクトリに以下を配置：

- `NotoSansJP-Light.ttf`
- `NotoSansJP-Regular.ttf`
- `NotoSansJP-Bold.ttf`
- `NotoSerifJP-Light.ttf`
- `NotoSerifJP-Regular.ttf`
- `NotoSerifJP-Bold.ttf`

## JSON レイアウト構造

```json
{
  "metadata": {
    "name": "テンプレート名",
    "version": "1.0.0",
    "description": "説明"
  },
  "card": {
    "width_mm": 91,
    "height_mm": 55,
    "background": "#FFFFFF",
    "background_image": "../assets/card_background.png"
  },
  "elements": [
    {
      "id": "要素ID",
      "type": "text",
      "content": "テキスト内容または{{PLACEHOLDER}}",
      "position": { "x_mm": 10, "y_mm": 8 },
      "font": {
        "category": "gothic",
        "size_pt": 9,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    }
  ]
}
```

## 背景画像

`card` セクションに `background_image` を指定すると、背景として画像を使用できます。

- 画像ファイルパスはテンプレートからの相対パスまたは絶対パス
- プレースホルダー `{{PLACEHOLDER}}` 形式に対応
- 背景画像は名刺サイズにリサイズされて配置
- `background`（背景色）より優先される

### 背景画像を使う場合のテンプレート構成

背景画像に会社ロゴや装飾を含め、テキスト要素のみをテンプレートで配置する方式が推奨されます。
この方式により、ロゴ画像の切り出しや位置調整の手間を省けます。

```
assets/card_background.png  ← ロゴ・装飾入りの背景画像
templates/xxx.json          ← テキスト要素のみを定義
```

## サイズ・位置の目安

### 名刺サイズ
- 幅: 91mm
- 高さ: 55mm
- 解像度: 300 DPI（1075 x 650 px）

### フォントサイズの目安

| 要素 | サイズ (pt) | 備考 |
|-----|------------|------|
| 氏名（漢字） | 12-16 | 最も目立つ要素 |
| 会社名 | 8-10 | 氏名より小さく |
| 役職・部署 | 7-9 | 補助情報 |
| 連絡先 | 6-8 | 住所、電話、メール等 |

### 位置の目安（y_mm）

| 領域 | y_mm | 配置する要素 |
|-----|------|-------------|
| 上部 | 5-15 | 会社名、部署 |
| 中央 | 20-35 | 氏名、役職 |
| 下部 | 40-52 | 連絡先情報 |

## トラブルシューティング

### フォントが見つからない

```
Error: Font not found: gothic/regular. Searched in: fonts
```

**解決方法:**
1. `fonts/` ディレクトリにフォントファイルが配置されているか確認
2. ファイル名が正しいか確認（`NotoSansJP-Regular.ttf` など）
3. `--font-path` で別のディレクトリを指定

### JSON パースエラー

```
Error: Invalid JSON - ...
```

**解決方法:**
1. JSON 構文が正しいか確認（カンマ、括弧など）
2. ファイルが UTF-8 エンコーディングか確認

### プレースホルダーが置換されない

`{{NAME}}` がそのまま出力される場合：

**解決方法:**
1. `--set` の KEY 名が正しいか確認（大文字小文字を区別）
2. プレースホルダー形式が `{{KEY}}` になっているか確認

### 出力ディレクトリが存在しない

出力先ディレクトリは自動作成されます。エラーが出る場合は書き込み権限を確認してください。
