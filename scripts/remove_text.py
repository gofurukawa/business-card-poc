#!/usr/bin/env python3
"""
名刺画像からテキストを除去して背景画像を生成するスクリプト

使用方法:
  # 手動で領域を指定（割合: x1,y1,x2,y2）
  python scripts/remove_text.py input/card.png -o output/bg.png \
    --region 0.28,0.12,0.95,0.95

  # 複数領域を指定
  python scripts/remove_text.py input/card.png -o output/bg.png \
    --region 0.28,0.12,0.95,0.52 \
    --region 0.28,0.52,0.95,0.95

  # 自動検出モード（白背景上のテキストを検出）
  python scripts/remove_text.py input/card.png -o output/bg.png --auto

  # 自動検出 + 除外領域を指定
  python scripts/remove_text.py input/card.png -o output/bg.png --auto \
    --exclude 0,0,0.35,0.15 \
    --exclude 0,0.65,0.35,1.0

  # 塗りつぶし色を指定（デフォルト: 白）
  python scripts/remove_text.py input/card.png -o output/bg.png \
    --region 0.28,0.12,0.95,0.95 --fill-color "#FFFFFF"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


def parse_region(region_str: str) -> tuple[float, float, float, float]:
    """
    領域文字列をパース

    Args:
        region_str: "x1,y1,x2,y2" 形式（0.0-1.0の割合）

    Returns:
        (x1, y1, x2, y2) タプル
    """
    parts = region_str.split(",")
    if len(parts) != 4:
        raise ValueError(f"Invalid region format: {region_str}. Expected: x1,y1,x2,y2")
    return tuple(float(p.strip()) for p in parts)


def parse_color(color_str: str) -> tuple[int, int, int]:
    """
    色文字列をパース

    Args:
        color_str: "#RRGGBB" 形式

    Returns:
        (B, G, R) タプル（OpenCV形式）
    """
    color_str = color_str.lstrip("#")
    if len(color_str) != 6:
        raise ValueError(f"Invalid color format: {color_str}. Expected: #RRGGBB")
    r = int(color_str[0:2], 16)
    g = int(color_str[2:4], 16)
    b = int(color_str[4:6], 16)
    return (b, g, r)  # OpenCV uses BGR


def create_region_mask(
    img_shape: tuple[int, int],
    regions: list[tuple[float, float, float, float]],
) -> np.ndarray:
    """
    指定された領域のマスクを作成

    Args:
        img_shape: (height, width)
        regions: [(x1, y1, x2, y2), ...] 形式（0.0-1.0の割合）

    Returns:
        マスク画像（白=対象領域）
    """
    h, w = img_shape
    mask = np.zeros((h, w), dtype=np.uint8)

    for x1, y1, x2, y2 in regions:
        pt1 = (int(w * x1), int(h * y1))
        pt2 = (int(w * x2), int(h * y2))
        cv2.rectangle(mask, pt1, pt2, 255, -1)

    return mask


def auto_detect_text_regions(
    img: np.ndarray,
    exclude_regions: list[tuple[float, float, float, float]] | None = None,
    bg_threshold: int = 230,
    text_threshold: int = 200,
    dilate_iterations: int = 3,
) -> np.ndarray:
    """
    白背景上のテキスト領域を自動検出

    Args:
        img: 入力画像 (BGR)
        exclude_regions: 除外する領域のリスト
        bg_threshold: 白背景の閾値（これより高い値が白背景）
        text_threshold: テキストの閾値（これより低い値がテキスト）
        dilate_iterations: マスク膨張の回数

    Returns:
        マスク画像（白=テキスト領域）
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 白背景領域を検出（高い値=白い部分）
    _, white_region = cv2.threshold(gray, bg_threshold, 255, cv2.THRESH_BINARY)

    # 白背景領域を膨張させて、テキスト周辺も含める
    kernel_bg = np.ones((10, 10), dtype=np.uint8)
    white_region_expanded = cv2.dilate(white_region, kernel_bg, iterations=2)

    # テキスト（暗いピクセル）を検出
    _, dark_pixels = cv2.threshold(gray, text_threshold, 255, cv2.THRESH_BINARY_INV)

    # 白背景領域内のテキストのみを対象
    text_mask = cv2.bitwise_and(dark_pixels, white_region_expanded)

    # 除外領域を適用
    if exclude_regions:
        exclude_mask = create_region_mask((h, w), exclude_regions)
        exclude_mask_inv = cv2.bitwise_not(exclude_mask)
        text_mask = cv2.bitwise_and(text_mask, exclude_mask_inv)

    # テキストマスクを膨張させて確実にカバー
    if dilate_iterations > 0:
        kernel = np.ones((3, 3), dtype=np.uint8)
        text_mask = cv2.dilate(text_mask, kernel, iterations=dilate_iterations)

    return text_mask


def remove_text(
    input_path: str,
    output_path: str,
    regions: list[tuple[float, float, float, float]] | None = None,
    auto_detect: bool = False,
    exclude_regions: list[tuple[float, float, float, float]] | None = None,
    fill_color: tuple[int, int, int] = (255, 255, 255),
    bg_threshold: int = 230,
    text_threshold: int = 200,
    dilate_iterations: int = 3,
    mask_output: str | None = None,
) -> None:
    """
    画像からテキストを除去

    Args:
        input_path: 入力画像パス
        output_path: 出力画像パス
        regions: 手動指定の領域リスト
        auto_detect: 自動検出モード
        exclude_regions: 自動検出時の除外領域
        fill_color: 塗りつぶし色 (BGR)
        bg_threshold: 自動検出の白背景閾値
        text_threshold: 自動検出のテキスト閾値
        dilate_iterations: マスク膨張回数
        mask_output: マスク画像の出力パス（デバッグ用）
    """
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"画像が読み込めません: {input_path}")

    h, w = img.shape[:2]
    print(f"画像サイズ: {w}x{h}")

    # マスクを作成
    if regions:
        # 手動指定モード
        mask = create_region_mask((h, w), regions)
        print(f"手動指定領域: {len(regions)}個")
    elif auto_detect:
        # 自動検出モード
        mask = auto_detect_text_regions(
            img,
            exclude_regions=exclude_regions,
            bg_threshold=bg_threshold,
            text_threshold=text_threshold,
            dilate_iterations=dilate_iterations,
        )
        print("自動検出モード")
        if exclude_regions:
            print(f"除外領域: {len(exclude_regions)}個")
    else:
        raise ValueError("--region または --auto を指定してください")

    # マスクを保存（デバッグ用）
    if mask_output:
        cv2.imwrite(mask_output, mask)
        print(f"マスク画像を保存: {mask_output}")

    # 塗りつぶし
    result = img.copy()
    result[mask > 0] = fill_color

    # 結果を保存
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, result)
    print(f"処理完了: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="名刺画像からテキストを除去して背景画像を生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 手動で領域を指定
  %(prog)s input/card.png -o output/bg.png --region 0.28,0.12,0.95,0.95

  # 自動検出モード
  %(prog)s input/card.png -o output/bg.png --auto

  # 自動検出 + 除外領域
  %(prog)s input/card.png -o output/bg.png --auto --exclude 0,0,0.35,0.15
        """,
    )
    parser.add_argument("input", help="入力画像パス")
    parser.add_argument("-o", "--output", required=True, help="出力画像パス")
    parser.add_argument(
        "--region",
        action="append",
        dest="regions",
        metavar="x1,y1,x2,y2",
        help="塗りつぶす領域（割合: 0.0-1.0）。複数指定可",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="白背景上のテキストを自動検出",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        dest="excludes",
        metavar="x1,y1,x2,y2",
        help="自動検出時に除外する領域（割合: 0.0-1.0）。複数指定可",
    )
    parser.add_argument(
        "--fill-color",
        default="#FFFFFF",
        metavar="COLOR",
        help="塗りつぶし色（#RRGGBB形式、デフォルト: #FFFFFF）",
    )
    parser.add_argument(
        "--bg-threshold",
        type=int,
        default=230,
        help="自動検出の白背景閾値（0-255、デフォルト: 230）",
    )
    parser.add_argument(
        "--text-threshold",
        type=int,
        default=200,
        help="自動検出のテキスト閾値（0-255、デフォルト: 200）",
    )
    parser.add_argument(
        "--dilate",
        type=int,
        default=3,
        help="マスク膨張回数（デフォルト: 3）",
    )
    parser.add_argument(
        "--mask",
        metavar="PATH",
        help="マスク画像の出力パス（デバッグ用）",
    )

    args = parser.parse_args()

    # 引数の検証
    if not args.regions and not args.auto:
        parser.error("--region または --auto を指定してください")

    if args.regions and args.auto:
        parser.error("--region と --auto は同時に指定できません")

    if args.excludes and not args.auto:
        parser.error("--exclude は --auto と一緒に使用してください")

    try:
        # 領域をパース
        regions = None
        if args.regions:
            regions = [parse_region(r) for r in args.regions]

        exclude_regions = None
        if args.excludes:
            exclude_regions = [parse_region(r) for r in args.excludes]

        fill_color = parse_color(args.fill_color)

        remove_text(
            args.input,
            args.output,
            regions=regions,
            auto_detect=args.auto,
            exclude_regions=exclude_regions,
            fill_color=fill_color,
            bg_threshold=args.bg_threshold,
            text_threshold=args.text_threshold,
            dilate_iterations=args.dilate,
            mask_output=args.mask,
        )
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
