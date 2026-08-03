"""ConfigParser로 CLI와 동일한 설정 흐름을 사용하는 예제."""

from __future__ import annotations

import argparse
from pathlib import Path

from marker.config.parser import ConfigParser
from marker.models import create_model_dict, shutdown_models
from marker.output import text_from_rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="설정 기반 Marker 변환")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("markdown", "json", "html", "chunks"), default="json")
    parser.add_argument("--pages", help='0-based 범위. 예: "0,2-4"')
    parser.add_argument("--output", type=Path, default=Path("result.json"))
    parser.add_argument("--mode", choices=("fast", "balanced"), default="fast")
    parser.add_argument("--extract-images", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    options = {
        "mode": args.mode,
        "output_format": args.format,
        "page_range": args.pages,
        "disable_image_extraction": not args.extract_images,
        "use_llm": False,
        "processors": None,
        "converter_cls": None,
        "llm_service": None,
    }
    parser = ConfigParser(options)
    artifacts = create_model_dict()
    try:
        converter_class = parser.get_converter_cls()
        converter = converter_class(
            config=parser.generate_config_dict(),
            artifact_dict=artifacts,
            processor_list=parser.get_processors(),
            renderer=parser.get_renderer(),
            llm_service=parser.get_llm_service(),
        )
        rendered = converter(str(input_path))
        text, extension, _ = text_from_rendered(rendered)

        output_path = args.output.resolve()
        if output_path.suffix.lower() != f".{extension}":
            output_path = output_path.with_suffix(f".{extension}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        print(f"output={output_path}")
        print(f"pages={converter.page_count}, format={args.format}")
    finally:
        shutdown_models(artifacts)


if __name__ == "__main__":
    main()
