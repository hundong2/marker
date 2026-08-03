"""Marker의 최소 Python 변환 예제.

실행 예:
    python guide/examples/basic_conversion.py sample.pdf --mode fast --disable-ocr
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict, shutdown_models
from marker.output import text_from_rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="문서를 Marker로 Markdown 변환")
    parser.add_argument("input", type=Path, help="입력 PDF 또는 지원 문서")
    parser.add_argument("--output-dir", type=Path, default=Path("out"))
    parser.add_argument("--mode", choices=("fast", "balanced"), default="fast")
    parser.add_argument(
        "--disable-ocr",
        action="store_true",
        help="VLM 호출을 모두 끕니다. scan 문서에는 사용하지 마세요.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    output_dir = args.output_dir.resolve() / input_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    config = {"mode": args.mode, "disable_ocr": args.disable_ocr}
    artifacts = create_model_dict()
    try:
        converter = PdfConverter(artifact_dict=artifacts, config=config)
        rendered = converter(str(input_path))
        text, extension, images = text_from_rendered(rendered)

        output_path = output_dir / f"{input_path.stem}.{extension}"
        output_path.write_text(text, encoding="utf-8")
        (output_dir / f"{input_path.stem}_meta.json").write_text(
            json.dumps(rendered.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        for image_name, image in images.items():
            # Renderer가 준 이름에서 directory 부분을 버려 output_dir 밖 쓰기를 막습니다.
            image.save(output_dir / Path(image_name).name)

        print(f"output={output_path}")
        print(f"characters={len(text)}, images={len(images)}")
        print(f"metadata_keys={sorted(rendered.metadata)}")
    finally:
        shutdown_models(artifacts)


if __name__ == "__main__":
    main()
