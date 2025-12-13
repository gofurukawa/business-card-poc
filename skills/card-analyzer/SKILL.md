# Card Analyzer Skill

名刺画像を解析し、レイアウト JSON を生成するスキルです。

## 概要

Claude の Vision 機能を使用して名刺画像を解析し、`schemas/card_layout.schema.json` に準拠した JSON を生成します。

## 解析手順

### Step 1: 画像からテキスト要素を識別

名刺画像を観察し、以下の要素を識別します：

| 要素 | 識別のヒント |
|-----|-------------|
| 氏名（漢字） | 最も大きい日本語テキスト。通常は中央付近 |
| 氏名（ふりがな/ローマ字） | 氏名の上または下にある小さいテキスト |
| 役職 | 氏名の近くにある肩書き（部長、課長、エンジニア等） |
| 部署名 | 会社名の下、または役職の近く |
| 会社名 | 上部に配置されることが多い。ロゴと併記の場合も |
| 郵便番号 | 〒マーク付き、または 000-0000 形式 |
| 住所 | 都道府県から始まる住所 |
| 電話番号 | TEL:、Tel:、電話 などのラベル付き |
| FAX番号 | FAX:、Fax: などのラベル付き |
| メールアドレス | @ を含むテキスト |
| URL | http:// または www. で始まるテキスト |

### Step 2: 各要素のレイアウト分析

識別した各要素について、以下を推定します：

#### 位置 (position)

名刺サイズは 91mm × 55mm です。画像上の相対位置から mm 単位で推定します。

```
x_mm: 左端からの距離（0-91）
y_mm: 上端からの距離（0-55）
```

**位置推定の目安:**
- 左端付近: x_mm = 5-15
- 中央: x_mm = 40-50
- 右端付近: x_mm = 70-85
- 上部: y_mm = 5-15
- 中央: y_mm = 20-35
- 下部: y_mm = 40-52

#### 配置 (align)

テキストの配置を判断します：
- `left`: 左揃え（最も一般的）
- `center`: 中央揃え（会社名や氏名で使用されることがある）
- `right`: 右揃え（連絡先情報で使用されることがある）

#### フォント (font)

**カテゴリ (category):**

| 見た目 | category | 説明 |
|-------|----------|------|
| 角ばった線、均一な太さ | `gothic` | ゴシック体（サンセリフ） |
| 線の強弱、ハネ・ハライがある | `mincho` | 明朝体（セリフ） |

**サイズ推定 (size_pt):**

| 要素タイプ | 推定サイズ | 備考 |
|-----------|-----------|------|
| 氏名（漢字） | 12-16 pt | 最も大きい要素 |
| 会社名 | 8-11 pt | 氏名より小さい |
| 役職・部署 | 7-9 pt | 中程度 |
| 連絡先（住所、電話等） | 6-8 pt | 小さめ |
| 注釈・補足 | 5-6 pt | 最も小さい |

**ウェイト (weight):**

| 見た目 | weight |
|-------|--------|
| 細い線 | `light` |
| 標準的な太さ | `regular` |
| 太い線、強調されている | `bold` |

**色 (color):**

色を #RRGGBB 形式で推定します：

| 見た目 | color |
|-------|-------|
| 黒 | `#000000` |
| 濃いグレー | `#333333` |
| グレー | `#666666` |
| 薄いグレー | `#999999` |
| 紺色 | `#000066` |
| 赤 | `#CC0000` |

### Step 3: JSON 出力

`schemas/card_layout.schema.json` に準拠した形式で出力します。

#### 出力テンプレート

```json
{
  "metadata": {
    "name": "analyzed_card",
    "version": "1.0.0",
    "description": "名刺画像から解析して生成"
  },
  "card": {
    "width_mm": 91,
    "height_mm": 55,
    "background": "#FFFFFF"
  },
  "elements": [
    {
      "id": "company_name",
      "type": "text",
      "content": "{{COMPANY_NAME}}",
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

#### 要素ID命名規則

| 要素 | id | プレースホルダー |
|-----|-----|-----------------|
| 会社名 | `company_name` | `{{COMPANY_NAME}}` |
| 部署名 | `department` | `{{DEPARTMENT}}` |
| 氏名（漢字） | `name_kanji` | `{{NAME_KANJI}}` |
| 氏名（ふりがな） | `name_furigana` | `{{NAME_FURIGANA}}` |
| 氏名（ローマ字） | `name_romaji` | `{{NAME_ROMAJI}}` |
| 役職 | `title` | `{{TITLE}}` |
| 郵便番号 | `postal_code` | `{{POSTAL_CODE}}` |
| 住所 | `address` | `{{ADDRESS}}` |
| 住所2行目 | `address2` | `{{ADDRESS2}}` |
| 電話番号 | `phone` | `{{PHONE}}` |
| FAX番号 | `fax` | `{{FAX}}` |
| 携帯番号 | `mobile` | `{{MOBILE}}` |
| メール | `email` | `{{EMAIL}}` |
| URL | `url` | `{{URL}}` |

## 判断基準の詳細

### フォントカテゴリの判別

**ゴシック体 (gothic) の特徴:**
- 線の太さが均一
- 角が直角的
- モダンでシンプルな印象
- 例: ゴシック、メイリオ、ヒラギノ角ゴ

**明朝体 (mincho) の特徴:**
- 横線が細く、縦線が太い
- ウロコ（セリフ）がある
- ハネ、ハライが特徴的
- フォーマルで伝統的な印象
- 例: 明朝、游明朝、ヒラギノ明朝

### 背景色の判定

- 白背景: `#FFFFFF`
- クリーム色: `#FFFFF0` または `#FFFEF0`
- 薄いグレー: `#F5F5F5`
- その他の色: 最も近い色を #RRGGBB で推定

### 複数行テキストの扱い

住所などが複数行にわたる場合：
- 各行を別要素として定義
- id に連番を付ける（`address`, `address2`）

## 出力例

### 入力画像の例（架空）

```
┌─────────────────────────────────────┐
│  株式会社サンプル                      │
│  営業部                               │
│                                      │
│      田中 太郎                        │
│      Taro Tanaka                     │
│      営業部長                         │
│                                      │
│  〒100-0001                          │
│  東京都千代田区...    TEL: 03-1234-... │
│                      t.tanaka@...    │
└─────────────────────────────────────┘
```

### 出力 JSON

```json
{
  "metadata": {
    "name": "analyzed_card",
    "version": "1.0.0",
    "description": "名刺画像から解析して生成"
  },
  "card": {
    "width_mm": 91,
    "height_mm": 55,
    "background": "#FFFFFF"
  },
  "elements": [
    {
      "id": "company_name",
      "type": "text",
      "content": "{{COMPANY_NAME}}",
      "position": { "x_mm": 8, "y_mm": 6 },
      "font": {
        "category": "gothic",
        "size_pt": 9,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "department",
      "type": "text",
      "content": "{{DEPARTMENT}}",
      "position": { "x_mm": 8, "y_mm": 12 },
      "font": {
        "category": "gothic",
        "size_pt": 7,
        "weight": "light",
        "color": "#666666"
      },
      "align": "left"
    },
    {
      "id": "name_kanji",
      "type": "text",
      "content": "{{NAME_KANJI}}",
      "position": { "x_mm": 20, "y_mm": 22 },
      "font": {
        "category": "mincho",
        "size_pt": 14,
        "weight": "bold",
        "color": "#000000"
      },
      "align": "left"
    },
    {
      "id": "name_romaji",
      "type": "text",
      "content": "{{NAME_ROMAJI}}",
      "position": { "x_mm": 20, "y_mm": 29 },
      "font": {
        "category": "gothic",
        "size_pt": 7,
        "weight": "regular",
        "color": "#666666"
      },
      "align": "left"
    },
    {
      "id": "title",
      "type": "text",
      "content": "{{TITLE}}",
      "position": { "x_mm": 20, "y_mm": 35 },
      "font": {
        "category": "gothic",
        "size_pt": 8,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "postal_code",
      "type": "text",
      "content": "〒{{POSTAL_CODE}}",
      "position": { "x_mm": 8, "y_mm": 44 },
      "font": {
        "category": "gothic",
        "size_pt": 6,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "phone",
      "type": "text",
      "content": "TEL: {{PHONE}}",
      "position": { "x_mm": 55, "y_mm": 44 },
      "font": {
        "category": "gothic",
        "size_pt": 6,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "email",
      "type": "text",
      "content": "{{EMAIL}}",
      "position": { "x_mm": 55, "y_mm": 48 },
      "font": {
        "category": "gothic",
        "size_pt": 6,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    }
  ]
}
```

## 注意事項

1. **推定値であることを明記**: 位置やサイズは推定値です。生成後に微調整が必要な場合があります。

2. **読み取れない要素**: 画像が不鮮明で読み取れない要素がある場合は、その旨をコメントで伝えてください。

3. **特殊なレイアウト**: 縦書き、斜めテキスト、ロゴ画像などは現在サポート外です。

4. **プライバシー配慮**: 実際の個人情報は出力せず、必ずプレースホルダー形式 `{{KEY}}` で出力してください。
