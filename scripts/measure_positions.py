#!/usr/bin/env python3
"""
名刺画像のテキスト位置を測定するスクリプト

使用例:
    # 単一画像の測定
    python scripts/measure_positions.py input/card.png

    # 2つの画像を比較
    python scripts/measure_positions.py input/original.png output/generated.png
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

try:
    import numpy as np
except ImportError:
    print("Error: numpy が必要です。pip install numpy でインストールしてください。")
    sys.exit(1)


# 名刺の標準サイズ (mm)
CARD_WIDTH_MM = 91
CARD_HEIGHT_MM = 55


def find_text_regions(img_path: Path, threshold: int = 200) -> list[dict]:
    """
    画像内のテキスト領域を検出する

    Args:
        img_path: 画像ファイルのパス
        threshold: テキスト検出の閾値（これより暗いピクセルをテキストとみなす）

    Returns:
        各テキスト領域の情報を含む辞書のリスト
    """
    img = Image.open(img_path).convert("L")
    pixels = np.array(img)
    h, w = pixels.shape

    px_per_mm_x = w / CARD_WIDTH_MM
    px_per_mm_y = h / CARD_HEIGHT_MM

    # 縦方向スキャン: テキストがある行を検出
    text_rows = []
    for y in range(h):
        if pixels[y, :].min() < threshold:
            text_rows.append(y)

    # テキスト領域をグループ化
    groups = []
    if text_rows:
        start = text_rows[0]
        prev = text_rows[0]
        for y in text_rows[1:]:
            if y - prev > 5:  # 5ピクセル以上離れていたら新しいグループ
                groups.append((start, prev))
                start = y
            prev = y
        groups.append((start, prev))

    # 各領域の詳細情報を収集
    regions = []
    for y_start, y_end in groups:
        # 左端を検出
        region = pixels[y_start : y_end + 1, :]
        left_px = 0
        for x in range(w):
            if region[:, x].min() < threshold:
                left_px = x
                break

        regions.append(
            {
                "y_start_px": y_start,
                "y_end_px": y_end,
                "x_left_px": left_px,
                "y_mm": y_start / px_per_mm_y,
                "x_mm": left_px / px_per_mm_x,
                "height_mm": (y_end - y_start) / px_per_mm_y,
            }
        )

    return regions


def print_regions(regions: list[dict], label: str = "") -> None:
    """テキスト領域の情報を表示"""
    if label:
        print(f"\n=== {label} ===\n")

    print(f"{'No.':<5} {'X (mm)':<10} {'Y (mm)':<10} {'高さ (mm)':<10}")
    print("-" * 40)

    for i, region in enumerate(regions, 1):
        print(
            f"{i:<5} {region['x_mm']:<10.1f} {region['y_mm']:<10.1f} {region['height_mm']:<10.1f}"
        )


def compare_regions(
    orig_regions: list[dict], gen_regions: list[dict]
) -> None:
    """2つの画像のテキスト領域を比較"""
    print("\n=== 位置比較 ===\n")
    print(
        f"{'No.':<5} {'元X':<8} {'生成X':<8} {'X差':<8} "
        f"{'元Y':<8} {'生成Y':<8} {'Y差':<8} "
        f"{'元高':<6} {'生成高':<6} {'高差':<6}"
    )
    print("-" * 80)

    count = min(len(orig_regions), len(gen_regions))
    max_x_diff = 0
    max_y_diff = 0
    max_h_diff = 0

    for i in range(count):
        orig = orig_regions[i]
        gen = gen_regions[i]

        x_diff = gen["x_mm"] - orig["x_mm"]
        y_diff = gen["y_mm"] - orig["y_mm"]
        h_diff = gen["height_mm"] - orig["height_mm"]

        max_x_diff = max(max_x_diff, abs(x_diff))
        max_y_diff = max(max_y_diff, abs(y_diff))
        max_h_diff = max(max_h_diff, abs(h_diff))

        print(
            f"{i+1:<5} {orig['x_mm']:<8.1f} {gen['x_mm']:<8.1f} {x_diff:+.1f}   "
            f"{orig['y_mm']:<8.1f} {gen['y_mm']:<8.1f} {y_diff:+.1f}   "
            f"{orig['height_mm']:<6.1f} {gen['height_mm']:<6.1f} {h_diff:+.1f}"
        )

    print("\n=== 精度評価 ===")
    print(f"X位置の最大誤差: {max_x_diff:.2f}mm")
    print(f"Y位置の最大誤差: {max_y_diff:.2f}mm")
    print(f"高さの最大誤差:  {max_h_diff:.2f}mm")

    if max_x_diff <= 0.5 and max_y_diff <= 0.5:
        print("\n✓ 位置精度は許容範囲内（±0.5mm以内）です")
    else:
        print("\n⚠ 位置精度が許容範囲外です。調整が必要です")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="名刺画像のテキスト位置を測定・比較する"
    )
    parser.add_argument(
        "image1",
        type=Path,
        help="測定する画像ファイル（または比較時の元画像）",
    )
    parser.add_argument(
        "image2",
        type=Path,
        nargs="?",
        help="比較する生成画像（省略時は単一画像の測定のみ）",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=200,
        help="テキスト検出の閾値（デフォルト: 200）",
    )

    args = parser.parse_args()

    # 画像1の測定
    if not args.image1.exists():
        print(f"Error: ファイルが見つかりません: {args.image1}")
        return 1

    regions1 = find_text_regions(args.image1, args.threshold)
    print_regions(regions1, str(args.image1))

    # 比較モード
    if args.image2:
        if not args.image2.exists():
            print(f"Error: ファイルが見つかりません: {args.image2}")
            return 1

        regions2 = find_text_regions(args.image2, args.threshold)
        print_regions(regions2, str(args.image2))
        compare_regions(regions1, regions2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
