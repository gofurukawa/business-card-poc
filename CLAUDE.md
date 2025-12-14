# Business Card Generator PoC

## 概要
JSON レイアウト定義から日本語対応の名刺画像（PNG）を生成する PoC プロジェクトです。

## 技術スタック
- Python 3.10+
- Pillow (PIL Fork) - 画像生成
- OpenCV - 画像処理（テキスト除去）
- 日本語フォント: Noto Sans JP (ゴシック) / Noto Serif JP (明朝)

## ディレクトリ構成
```
business-card-poc/
├── CLAUDE.md              # このファイル
├── skills/
│   ├── card-analyzer/     # 名刺解析スキル
│   └── card-generator/    # 名刺生成スキル
├── src/
│   └── generator.py       # 名刺画像生成エンジン
├── scripts/
│   ├── backup_version.sh  # バージョン管理付きバックアップスクリプト
│   └── remove_text.py     # 名刺画像からテキストを除去して背景画像を生成
├── schemas/
│   └── card_layout.schema.json  # レイアウト JSON スキーマ
├── templates/
│   ├── sample_card.json          # サンプル名刺（デフォルト値入り）
│   └── sample_card_template.json # サンプル名刺（プレースホルダー形式）
├── assets/                # 画像ファイル格納ディレクトリ（自由に配置可能）
├── fonts/                 # フォントファイル格納ディレクトリ
├── input/                 # スキャン画像入力用
└── output/                # 生成画像出力先
```

## スキル
- `skills/card-analyzer/SKILL.md` - 名刺画像の解析手順（Vision による JSON 生成）
- `skills/card-generator/SKILL.md` - 名刺画像の生成ワークフロー（JSON から PNG 生成）

## 名刺再現ワークフロー

名刺スキャン画像から似た名刺を再現する Agent フロー：

```
┌─────────────────────────────────────────────────────────────┐
│  1. ユーザーが input/ に名刺画像を配置                         │
│     └─ 例: input/scanned_card.png                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. card-analyzer スキルで解析                               │
│     └─ skills/card-analyzer/SKILL.md の手順に従い           │
│        画像を解析して JSON を生成                            │
│     └─ 出力: templates/analyzed_card.json                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. card-generator スキルで PNG 生成                         │
│     └─ python3 src/generator.py templates/analyzed_card.json │
│        -o output/generated_card.png                         │
│        --set COMPANY_NAME="..." --set NAME_KANJI="..." ...  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 元画像と生成画像を比較                                    │
│     └─ input/scanned_card.png と                            │
│        output/generated_card.png を並べて確認               │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────┐
                    │ 差異あり？   │
                    └─────────────┘
                     ↓ Yes      ↓ No
┌──────────────────────────┐    ┌────────────────────────────┐
│  5a. JSON を調整          │    │  5b. 完成                   │
│     └─ 位置、サイズ、     │    │     └─ output/ に保存完了   │
│        フォント等を修正   │    └────────────────────────────┘
│     └─ 再度 3. へ         │
└──────────────────────────┘
```

### ワークフロー実行例

```bash
# 1. 名刺画像を input/ に配置（ユーザー操作）

# 2. Claude に画像を見せて解析を依頼
#    → card-analyzer スキルに従い JSON を生成

# 3. 生成された JSON から名刺画像を作成
python3 src/generator.py templates/analyzed_card.json \
  -o output/generated_card.png \
  --set COMPANY_NAME="株式会社サンプル" \
  --set NAME_KANJI="山田 太郎" \
  # ... 他のプレースホルダーも指定

# 4. 比較・調整を繰り返し

# 5. 完成後、必要に応じてテンプレートを保存
```

## 開発時の注意点
- フォントパスは設定可能（デフォルト: `fonts/`、CLI引数 `--font-path` で変更可）
- 名刺サイズ: 91mm × 55mm（日本標準サイズ）
- 解像度: 300 DPI（印刷品質）
- JSON ファイルは UTF-8 エンコーディング必須
- プレースホルダー形式: `{{PLACEHOLDER_NAME}}`
- フォントが見つからない場合はエラーで停止
- 対応要素タイプ: `text`（テキスト）、`image`（画像）
- 画像パスはテンプレートファイルからの相対パスまたは絶対パス

## よく使うコマンド

```bash
# 依存関係インストール
pip install -r requirements.txt

# 基本的な使い方
python3 src/generator.py templates/sample_card.json -o output/card.png

# プレースホルダーを置換して生成
python3 src/generator.py templates/sample_card_template.json -o output/tanaka.png \
  --set NAME_KANJI="田中 太郎" \
  --set COMPANY_NAME="株式会社サンプル"

# カスタムフォントパスを指定
python3 src/generator.py templates/sample_card.json -o output/card.png \
  --font-path /usr/share/fonts/noto-cjk/

# バージョン管理付きでバックアップ（位置調整の反復時に便利）
./scripts/backup_version.sh templates/analyzed_card.json \
  --set NAME_KANJI="田中 太郎" \
  --set COMPANY_NAME="株式会社サンプル"

# 名刺画像からテキストを除去して背景画像を生成（手動領域指定）
python3 scripts/remove_text.py input/card.png -o assets/background.png \
  --region 0.28,0.08,0.98,0.98

# 名刺画像からテキストを除去（自動検出 + 除外領域）
python3 scripts/remove_text.py input/card.png -o assets/background.png \
  --auto --exclude 0,0,0.28,1.0
```
