# Card Analyzer Skill

名刺画像を解析し、レイアウト JSON を生成するスキルです。

## 概要

Claude の Vision 機能を使用して名刺画像を解析し、`schemas/card_layout.schema.json` に準拠した JSON を生成します。

## 解析手順

### Step 1: 画像の基準サイズを確認

名刺の標準サイズは **91mm × 55mm** です。画像内の要素位置を正確に推定するため、以下の計算式を使用します：

```
x_mm = (要素の左端位置 / 画像幅) × 91
y_mm = (要素の上端位置 / 画像高さ) × 55
```

**重要**: 位置は要素の**左上角**を基準とします。

### Step 2: 画像要素を識別

名刺画像内のグラフィック要素（ロゴ、写真、装飾帯など）を識別します。

#### 識別する画像要素

| 要素タイプ | 識別のヒント | 切り出し方針 |
|-----------|-------------|-------------|
| 会社ロゴ | 上部や角に配置、テキストと異なるグラフィック | 領域全体を1つの画像として切り出し |
| 写真エリア | グレーや色付きの四角形領域 | 領域全体を切り出し |
| 装飾帯・ライン | 画面端の色付き帯、横線など | 帯全体を1つの画像として切り出し |
| アイコン | 電話、メール等の小さいマーク | 必要に応じて切り出し |

**切り出しの原則**:
- 画像要素は**細かくスライスせず、領域全体を1つの画像**として切り出す
- ロゴと装飾帯が連続している場合も、それぞれ独立した画像として扱う
- 切り出した画像は `assets/` ディレクトリに保存

#### 画像要素の位置・サイズ推定

```
位置 (position):
  x_mm: 画像領域の左端位置 (mm)
  y_mm: 画像領域の上端位置 (mm)

サイズ (size):
  width_mm: 画像領域の幅 (mm)
  height_mm: 画像領域の高さ (mm) ※省略時はアスペクト比維持
```

### Step 3: テキスト要素を識別

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
| 資格・肩書 | 「○○士」「○○検定会員」など |

### Step 4: テキスト要素の位置を正確に推定

#### 位置計算の手順

1. **画像全体に対する要素の相対位置を測定**
   - 要素の左端が画像幅の何%の位置にあるか
   - 要素の上端が画像高さの何%の位置にあるか

2. **mm単位に変換**
   ```
   x_mm = (水平位置%) × 91 / 100
   y_mm = (垂直位置%) × 55 / 100
   ```

3. **小数点以下は四捨五入**（整数または0.5刻み）

#### 位置推定の具体例

```
画像解析例:
- 「会社名」が画像の左から55%、上から12%の位置にある場合:
  x_mm = 55% × 91 / 100 = 50mm
  y_mm = 12% × 55 / 100 = 7mm

- 「氏名」が画像の左から50%、上から25%の位置にある場合:
  x_mm = 50% × 91 / 100 = 45.5mm → 46mm
  y_mm = 25% × 55 / 100 = 13.75mm → 14mm
```

#### 配置 (align) の判断

テキストの配置を判断します：
- `left`: 左揃え（最も一般的）
- `center`: 中央揃え（会社名や氏名で使用されることがある）
- `right`: 右揃え（連絡先情報で使用されることがある）

**注意**: `position.x_mm` は配置の基準点を示します。
- `left`: x_mm はテキストの左端
- `center`: x_mm はテキストの中央
- `right`: x_mm はテキストの右端

### Step 5: フォント属性を推定

#### カテゴリ (category)

| 見た目 | category | 説明 |
|-------|----------|------|
| 角ばった線、均一な太さ | `gothic` | ゴシック体（サンセリフ） |
| 線の強弱、ハネ・ハライがある | `mincho` | 明朝体（セリフ） |

#### サイズ推定 (size_pt)

| 要素タイプ | 推定サイズ | 備考 |
|-----------|-----------|------|
| 氏名（漢字） | 14-20 pt | 最も大きい要素 |
| 会社名・支店名 | 9-12 pt | 氏名より小さい |
| 役職・部署 | 6-8 pt | 中程度 |
| 連絡先（住所、電話等） | 5-7 pt | 小さめ |
| 注釈・補足 | 4-6 pt | 最も小さい |

#### ウェイト (weight)

| 見た目 | weight |
|-------|--------|
| 細い線 | `light` |
| 標準的な太さ | `regular` |
| 太い線、強調されている | `bold` |

#### 色 (color)

色を #RRGGBB 形式で推定します：

| 見た目 | color |
|-------|-------|
| 黒 | `#000000` |
| 濃いグレー | `#333333` |
| グレー | `#666666` |
| 薄いグレー | `#999999` |
| 紺色（企業カラー等） | `#1a2e6e` |
| 赤 | `#CC0000` |

### Step 6: JSON 出力

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
      "id": "company_logo",
      "type": "image",
      "src": "../assets/company_logo.png",
      "position": { "x_mm": 2, "y_mm": 2 },
      "size": { "width_mm": 25 }
    },
    {
      "id": "company_name",
      "type": "text",
      "content": "{{COMPANY_NAME}}",
      "position": { "x_mm": 50, "y_mm": 8 },
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

**画像要素:**

| 要素 | id | src例 |
|-----|-----|------|
| 会社ロゴ | `company_logo` | `../assets/company_logo.png` |
| サブロゴ | `sub_logo` | `../assets/sub_logo.png` |
| 写真エリア | `photo_area` | `../assets/photo_placeholder.png` |
| 上部装飾帯 | `top_stripe` | `../assets/top_stripe.png` |
| 下部装飾帯 | `bottom_stripe` | `../assets/bottom_stripe.png` |
| 左側装飾 | `left_decoration` | `../assets/left_bar.png` |

**テキスト要素:**

| 要素 | id | プレースホルダー |
|-----|-----|-----------------|
| 会社名 | `company_name` | `{{COMPANY_NAME}}` |
| 支店名 | `branch` | `{{BRANCH}}` |
| 銀行名+支店名 | `bank_branch` | `{{BANK_NAME}} {{BRANCH}}` |
| 部署名 | `department` | `{{DEPARTMENT}}` |
| 氏名（漢字） | `name_kanji` | `{{NAME_KANJI}}` |
| 氏名（ふりがな） | `name_furigana` | `{{NAME_FURIGANA}}` |
| 氏名（ローマ字） | `name_romaji` | `{{NAME_ROMAJI}}` |
| 役職 | `title` | `{{TITLE}}` |
| 資格 | `qualification` | `{{QUALIFICATION}}` |
| 郵便番号+住所 | `address` | `〒{{POSTAL_CODE}} {{ADDRESS}}` |
| 住所2行目 | `address2` | `{{ADDRESS2}}` |
| 電話番号 | `phone` | `TEL：{{PHONE}}` |
| FAX番号 | `fax` | `FAX：{{FAX}}` |
| 携帯番号 | `mobile` | `{{MOBILE}}` |
| メール | `email` | `{{EMAIL}}` |
| URL | `url` | `{{URL}}` |

## 出力例

### 入力画像の例（銀行名刺風）

```
┌─────────────────────────────────────────────────────┐
│ [会社ロゴ]             信託業務課                     │
│                        課長                          │
│ ┌──────────┐                                        │
│ │          │           日本 太郎                    │
│ │ 写真     │           ○○検定会員                   │
│ │ エリア   │                                        │
│ │          │           サンプル信託銀行 新宿支店     │
│ └──────────┘                                        │
│ [サブロゴ]             〒160-0022 東京都新宿区...     │
│                        TEL：03-1234-5678            │
│ ████████████████████   FAX：03-1234-5679            │
└─────────────────────────────────────────────────────┘
```

### 位置計算例

上記画像を解析した場合：

| 要素 | 水平位置 | 垂直位置 | x_mm | y_mm |
|------|---------|---------|------|------|
| 会社ロゴ | 1% | 2% | 1 | 1 |
| 信託業務課 | 55% | 13% | 50 | 7 |
| 課長 | 55% | 18% | 50 | 10 |
| 日本 太郎 | 50% | 25% | 46 | 14 |
| サンプル信託銀行... | 44% | 53% | 40 | 29 |

### 出力 JSON

```json
{
  "metadata": {
    "name": "sample_bank_card",
    "version": "1.0.0",
    "description": "銀行名刺風サンプルから解析"
  },
  "card": {
    "width_mm": 91,
    "height_mm": 55,
    "background": "#FFFFFF"
  },
  "elements": [
    {
      "id": "company_logo",
      "type": "image",
      "src": "../assets/company_logo.png",
      "position": { "x_mm": 1, "y_mm": 1 },
      "size": { "width_mm": 23 }
    },
    {
      "id": "photo_area",
      "type": "image",
      "src": "../assets/photo_placeholder.png",
      "position": { "x_mm": 3, "y_mm": 9 },
      "size": { "width_mm": 21 }
    },
    {
      "id": "sub_logo",
      "type": "image",
      "src": "../assets/sub_logo.png",
      "position": { "x_mm": 1, "y_mm": 36 },
      "size": { "width_mm": 25 }
    },
    {
      "id": "bottom_stripe",
      "type": "image",
      "src": "../assets/bottom_stripe.png",
      "position": { "x_mm": 0, "y_mm": 51 },
      "size": { "width_mm": 91, "height_mm": 4 }
    },
    {
      "id": "department",
      "type": "text",
      "content": "{{DEPARTMENT}}",
      "position": { "x_mm": 50, "y_mm": 7 },
      "font": {
        "category": "gothic",
        "size_pt": 6,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "title",
      "type": "text",
      "content": "{{TITLE}}",
      "position": { "x_mm": 50, "y_mm": 10 },
      "font": {
        "category": "gothic",
        "size_pt": 6,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "name_kanji",
      "type": "text",
      "content": "{{NAME_KANJI}}",
      "position": { "x_mm": 46, "y_mm": 14 },
      "font": {
        "category": "gothic",
        "size_pt": 18,
        "weight": "bold",
        "color": "#000000"
      },
      "align": "left"
    },
    {
      "id": "qualification",
      "type": "text",
      "content": "{{QUALIFICATION}}",
      "position": { "x_mm": 46, "y_mm": 22 },
      "font": {
        "category": "gothic",
        "size_pt": 5,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "bank_branch",
      "type": "text",
      "content": "{{BANK_NAME}} {{BRANCH}}",
      "position": { "x_mm": 40, "y_mm": 29 },
      "font": {
        "category": "gothic",
        "size_pt": 10,
        "weight": "bold",
        "color": "#1a2e6e"
      },
      "align": "left"
    },
    {
      "id": "address",
      "type": "text",
      "content": "〒{{POSTAL_CODE}} {{ADDRESS}}",
      "position": { "x_mm": 40, "y_mm": 35 },
      "font": {
        "category": "gothic",
        "size_pt": 5,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "phone",
      "type": "text",
      "content": "TEL：{{PHONE}}（ダイヤルイン）",
      "position": { "x_mm": 40, "y_mm": 39 },
      "font": {
        "category": "gothic",
        "size_pt": 5,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    },
    {
      "id": "fax",
      "type": "text",
      "content": "FAX：{{FAX}}",
      "position": { "x_mm": 40, "y_mm": 43 },
      "font": {
        "category": "gothic",
        "size_pt": 5,
        "weight": "regular",
        "color": "#333333"
      },
      "align": "left"
    }
  ]
}
```

## 画像要素の切り出し手順

### 1. 画像領域を特定

名刺画像内で、テキスト以外のグラフィック要素を特定します：
- ロゴマーク（会社ロゴ、ブランドロゴ）
- 写真領域（人物写真用のプレースホルダー）
- 装飾帯（色付きのライン、ストライプ）
- アイコン類

### 2. 領域の境界を決定

各画像要素について、切り出す領域を決定します：
- **ロゴ**: ロゴ全体を含む最小の矩形領域
- **装飾帯**: 帯の開始から終了まで（全幅または全高）
- **写真領域**: 枠線を含む全体

### 3. Python で切り出し

```python
from PIL import Image

img = Image.open('input/card.png')
w, h = img.size

# 例: 上部ロゴ（左上の25%×12%の領域）
logo = img.crop((0, 0, int(w * 0.25), int(h * 0.12)))
logo.save('assets/company_logo.png')

# 例: 下部装飾帯（下から8%の領域、全幅）
stripe = img.crop((0, int(h * 0.92), w, h))
stripe.save('assets/bottom_stripe.png')
```

### 4. 単色の装飾は生成も可

装飾帯が単色の場合は、Pythonで生成することも可能です：

```python
from PIL import Image

# 91mm × 4mm @300dpi の青い帯
stripe = Image.new('RGB', (1075, 47), '#1a2e6e')
stripe.save('assets/bottom_stripe.png')
```

## 位置調整の反復プロセス

解析→生成→比較→調整を繰り返す際、変更履歴を残すことで比較しやすくなります。

### バックアップの管理

調整のたびに、JSONと生成画像を連番で保存します：

```
output/
├── backup/
│   ├── card_v01.json      # 初回解析結果
│   ├── card_v01.png       # 初回生成画像
│   ├── card_v02.json      # 位置調整後
│   ├── card_v02.png       # 調整後の生成画像
│   ├── card_v03.json      # さらに調整
│   └── card_v03.png
└── card.png               # 最新の生成画像
```

### バックアップスクリプトの使用

`scripts/backup_version.sh` を使用して、JSONと生成画像を連番でバックアップできます：

```bash
# 基本的な使い方
./scripts/backup_version.sh templates/analyzed_card.json \
  --set NAME_KANJI="田中 太郎" \
  --set COMPANY_NAME="株式会社サンプル"

# 出力例:
# Saved JSON: output/backup/analyzed_card_v01.json
# Saved Image: output/backup/analyzed_card_v01.png
```

実行するたびにバージョン番号が自動的にインクリメントされます（v01 → v02 → v03...）。

### 反復プロセスの流れ

```
1. 初回解析
   └─ JSON生成 → output/backup/card_v01.json
   └─ 画像生成 → output/backup/card_v01.png

2. 元画像と比較（目視）
   └─ input/original.png と output/backup/card_v01.png を並べて確認

3. 位置調整
   └─ JSON編集 → templates/analyzed_card.json を修正
   └─ バックアップ → output/backup/card_v02.json
   └─ 再生成 → output/backup/card_v02.png

4. 繰り返し
   └─ v01 → v02 → v03... と履歴が残る
   └─ 過去バージョンと比較して改善を確認
```

### 比較時のヒント

- **v01とv02を並べて表示**: 調整が正しい方向か確認
- **元画像と最新版を重ねる**: 透過度を変えて位置のずれを確認
- **問題があれば過去バージョンに戻る**: バックアップから復元可能

## 注意事項

1. **位置は比率から計算**: 画像上の位置を%で測定し、91mm × 55mm に変換する

2. **画像は領域全体を切り出す**: 細かくスライスせず、ロゴや帯は1つの画像として扱う

3. **プライバシー配慮**: 実際の個人情報は出力せず、必ずプレースホルダー形式 `{{KEY}}` で出力

4. **微調整が必要**: 推定値は目安です。生成後に元画像と比較し、位置を調整してください

5. **画像ファイルのパス**: テンプレートJSONからの相対パス（`../assets/xxx.png`）で指定

6. **バックアップを活用**: 調整の履歴を残し、過去バージョンと比較しながら改善する
