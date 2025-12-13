#!/bin/bash
# backup_version.sh - JSONテンプレートと生成画像をバージョン管理付きでバックアップ
#
# 使用方法:
#   ./scripts/backup_version.sh <テンプレートJSON> [--set KEY=VALUE ...]
#
# 例:
#   ./scripts/backup_version.sh templates/analyzed_card.json \
#     --set NAME_KANJI="田中 太郎" \
#     --set COMPANY_NAME="株式会社サンプル"

set -e

# 引数チェック
if [ $# -lt 1 ]; then
    echo "Usage: $0 <template.json> [--set KEY=VALUE ...]"
    echo ""
    echo "Example:"
    echo "  $0 templates/analyzed_card.json --set NAME_KANJI=\"田中 太郎\""
    exit 1
fi

TEMPLATE_JSON="$1"
shift  # 残りの引数は --set オプション

# テンプレートファイルの存在確認
if [ ! -f "$TEMPLATE_JSON" ]; then
    echo "Error: Template file not found: $TEMPLATE_JSON"
    exit 1
fi

# バックアップディレクトリ
BACKUP_DIR="output/backup"
mkdir -p "$BACKUP_DIR"

# テンプレート名からベース名を取得（拡張子なし）
TEMPLATE_BASENAME=$(basename "$TEMPLATE_JSON" .json)

# 次のバージョン番号を取得
LAST_NUM=$(ls "$BACKUP_DIR"/${TEMPLATE_BASENAME}_v*.json 2>/dev/null | \
    sed "s/.*_v\([0-9]*\)\.json/\1/" | \
    sort -n | \
    tail -1)
NEXT_NUM=$(printf "%02d" $((${LAST_NUM:-0} + 1)))

# ファイル名
BACKUP_JSON="$BACKUP_DIR/${TEMPLATE_BASENAME}_v${NEXT_NUM}.json"
BACKUP_PNG="$BACKUP_DIR/${TEMPLATE_BASENAME}_v${NEXT_NUM}.png"

# JSONをバックアップ
cp "$TEMPLATE_JSON" "$BACKUP_JSON"
echo "Saved JSON: $BACKUP_JSON"

# 画像を生成
echo "Generating image..."
python3 src/generator.py "$TEMPLATE_JSON" -o "$BACKUP_PNG" "$@"

echo ""
echo "=== Backup Complete ==="
echo "JSON:  $BACKUP_JSON"
echo "Image: $BACKUP_PNG"
echo ""
echo "To compare with previous version:"
echo "  open $BACKUP_DIR/${TEMPLATE_BASENAME}_v$(printf "%02d" $((NEXT_NUM - 1))).png $BACKUP_PNG"
