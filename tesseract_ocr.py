import sys
import argparse
from pathlib import Path

from PIL import Image
import pytesseract

# ====== 必要に応じて固定パスを指定（環境変数PATHが通っていない場合） ======
# 例:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_image(path: Path, lang: str) -> str:
    """1枚の画像をOCRしてテキストを返す"""
    with Image.open(path) as im:
        # 必要があれば前処理（グレースケール化など）を入れる
        # im = im.convert("L")
        text = pytesseract.image_to_string(im, lang=lang)
    # 後処理：末尾の余分な空行を整理
    return text.rstrip() + "\n"

def main():
    parser = argparse.ArgumentParser(
        description="指定フォルダ内の画像（png/jpg/jpeg）を一括OCRして同名のtxtを書き出します。"
    )
    parser.add_argument(
        "--dir",
        default=r"C:\Users\257045\Documents\Tesseract",
        help="画像が置いてあるディレクトリパス（デフォルト: %(default)s）",
    )
    parser.add_argument(
        "--lang",
        default="jpn+eng",
        help="Tesseractの言語コード（デフォルト: %(default)s）",
    )
    parser.add_argument(
        "--ext",
        default="png,jpg,jpeg",
        help="対象拡張子をカンマ区切りで指定（デフォルト: %(default)s）",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="テキスト出力の文字コード（デフォルト: %(default)s）",
    )
    args = parser.parse_args()

    target_dir = Path(args.dir)
    if not target_dir.exists():
        print(f"? 指定フォルダが存在しません: {target_dir}")
        sys.exit(1)

    exts = {"." + e.strip().lower().lstrip(".") for e in args.ext.split(",")}
    files = sorted([p for p in target_dir.iterdir() if p.suffix.lower() in exts])

    if not files:
        print(f"対象画像が見つかりませんでした（{', '.join(sorted(exts))}）。フォルダ: {target_dir}")
        sys.exit(0)

    ok, ng = 0, 0
    for img in files:
        try:
            print(f"[OCR] {img.name} ... ", end="", flush=True)
            text = ocr_image(img, lang=args.lang)
            out_txt = img.with_suffix(".txt")
            out_txt.write_text(text, encoding=args.encoding)
            print(f"-> {out_txt.name}")
            ok += 1
        except Exception as e:
            print("FAILED:", e)
            ng += 1

    print("\n=== 結果 ===")
    print(f"成功: {ok} 件 / 失敗: {ng} 件")
    print(f"出力先: {target_dir}")

if __name__ == "__main__":
    main()
