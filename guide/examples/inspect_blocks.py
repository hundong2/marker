"""최종 rendering 전에 Marker Document block tree를 검사하는 예제."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict, shutdown_models


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Marker block 구조 검사")
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=("fast", "balanced"), default="fast")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    artifacts = create_model_dict()
    try:
        converter = PdfConverter(
            artifact_dict=artifacts,
            config={"mode": args.mode},
        )
        document = converter.build_document(str(input_path))
        counts = Counter(block.block_type.value for block in document.contained_blocks())

        print(f"pages={len(document.pages)}")
        print("block counts:")
        for block_type, count in counts.most_common():
            print(f"  {block_type:24s} {count}")

        print("top-level page structures:")
        for page in document.pages:
            order = [block_id.block_type.value for block_id in page.structure]
            print(f"  page {page.page_id}: {' -> '.join(order)}")
    finally:
        shutdown_models(artifacts)


if __name__ == "__main__":
    main()
