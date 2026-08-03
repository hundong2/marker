<p align="center">
  <img src="data/images/datalab-logo.png" alt="Datalab 로고" width="150"/>
</p>
<h1 align="center">Marker</h1>
<p align="center"><strong>문서를 Markdown, JSON, chunks, HTML로 변환하는 Document Intelligence 도구</strong></p>

> [English](README.md) | [한국어 학습 가이드](guide/README.md)

이 문서는 원본 [`README.md`](README.md)의 구조와 핵심 정보를 보존한 한국어 번역·해설입니다. 설치 전에는 코드와 model weight의 license가 서로 다름을 반드시 확인하세요.

## Marker 소개

Marker는 다양한 문서를 빠르고 정확하게 구조화된 형식으로 변환합니다.

- PDF, image, PPTX, DOCX, XLSX, HTML, EPUB와 여러 언어 지원
- table, form, equation, inline math, link, reference, code block 처리
- image 추출과 저장
- header, footer 등 문서 artifact 제거
- custom processor와 renderer를 통한 확장
- 선택적인 LLM 보정과 custom prompt
- GPU, CPU, Apple Silicon MPS 지원

## 관리형 Datalab 플랫폼

Datalab의 관리형 플랫폼은 Marker보다 정확도가 높은 최신 open-source model인 [Chandra](https://github.com/datalab-to/chandra)를 사용합니다. 원문 기준 기본 zero data retention, SOC 2 Type 2와 custom BAA를 지원하며, 대량 batch 처리 서비스도 제공합니다. 제공 조건과 가격은 [공식 페이지](https://www.datalab.to/pricing)에서 최신 정보를 확인하세요.

## 성능

Marker는 math, table, multi-column, scan 등 1,403개 PDF를 다루는 제3자 benchmark [olmocr-bench](https://github.com/allenai/olmocr/tree/main/olmocr/bench)로 평가됩니다. 원문에 보고된 overall macro-average는 balanced 76.0%, fast 66.6%, fast/no-OCR 43.6%입니다. 이는 특정 hardware와 설정의 결과이므로 자신의 문서 분포에서 다시 측정해야 합니다.

| Mode | 적합한 환경 | 품질·비용 특성 |
|---|---|---|
| `balanced` | GPU, 수식·scan·복잡한 layout | VLM layout과 full-page OCR을 적극 사용 |
| `fast` | CPU/MPS 또는 born-digital 중심 | 경량 layout detector와 선택적 VLM 호출 |
| `--disable_ocr` | 깨끗한 digital PDF, 최저 비용 | VLM을 전혀 호출하지 않으며 scan·수식 품질 저하 |

## Hybrid mode

`--use_llm`을 사용하면 여러 page의 table 병합, inline math, form 값 추출과 복잡한 서식을 LLM으로 보정할 수 있습니다. Gemini, Claude, OpenAI-compatible, Azure OpenAI, Vertex, OpenRouter, Ollama를 지원합니다. 기본 service는 Gemini 계열입니다. 외부 API를 사용하면 문서 내용이 해당 제공자에게 전송될 수 있으므로 privacy·retention 정책을 확인하세요.

## License와 상업적 사용

- code: Apache License 2.0
- model weight: 수정된 AI Pubs OpenRAIL-M

model weight는 연구·개인 용도와 일정 규모 이하 startup에 별도 조건이 적용됩니다. 상업적 사용 전 [`MODEL_LICENSE`](MODEL_LICENSE)와 [Datalab pricing](https://www.datalab.to/pricing)을 직접 확인하세요. Apache 2.0 code license가 model weight까지 동일하게 허용한다는 뜻은 아닙니다.

## 설치

Python 3.10 이상과 [PyTorch](https://pytorch.org/get-started/locally/)가 필요합니다.

```shell
pip install marker-pdf
```

PDF 이외의 문서 형식도 처리하려면 다음 extra를 설치합니다.

```shell
pip install "marker-pdf[full]"
```

source checkout에서 개발하려면 `uv`를 권장합니다.

```shell
uv sync --group dev
```

### 추론 backend 사전 요구사항

Surya는 처음 필요할 때 inference server를 자동으로 시작합니다.

- NVIDIA GPU: Docker와 NVIDIA Container Toolkit, vLLM backend
- CPU/Apple Silicon: `llama-server` binary가 포함된 llama.cpp

주요 환경 변수:

| 변수 | 의미 |
|---|---|
| `SURYA_INFERENCE_URL` | 이미 실행 중인 OpenAI-compatible Surya server URL |
| `SURYA_INFERENCE_BACKEND` | `vllm` 또는 `llamacpp` |
| `SURYA_INFERENCE_PARALLEL` | 동시 요청 수 override |
| `SURYA_INFERENCE_KEEP_ALIVE` | 여러 실행 사이 server 유지 |
| `VLLM_GPUS` | vLLM에서 사용할 GPU index |
| `TORCH_DEVICE` | 작은 local model의 device 강제 지정 |

## 사용법

### GUI

```shell
pip install -U streamlit streamlit-ace
marker_gui
```

### 단일 파일

```shell
marker_single /path/to/file.pdf
```

중요 option:

- `--mode balanced|fast`: 품질·비용 mode 선택
- `--disable_ocr`: 모든 VLM 호출 비활성화
- `--page_range "0,5-10,20"`: 0-based page 범위
- `--output_format markdown|json|html|chunks`: 출력 형식
- `--output_dir PATH`: 저장 경로
- `--use_llm`: LLM 보정 사용
- `--force_ocr`: 모든 page를 OCR
- `--strip_existing_ocr`: 기존 OCR text를 제거하고 다시 OCR
- `--ocr_inline_math`: fast mode에서도 inline math OCR
- `--disable_image_extraction`: image 추출 비활성화
- `--processors`: full import path로 processor 목록 지정
- `--converter_cls`: `PdfConverter`, `TableConverter` 등 선택
- `--config_json`: 추가 설정 JSON
- `--debug`: layout image와 debug JSON 저장

예시:

```shell
# 깨끗한 digital PDF를 CPU에서 빠르게 처리
marker_single report.pdf --mode fast --disable_ocr --output_dir out

# scan과 수식이 많은 문서를 GPU에서 처리
marker_single paper.pdf --mode balanced --force_ocr --output_format markdown

# table만 JSON으로 추출
marker_single statement.pdf --converter_cls marker.converters.table.TableConverter --output_format json
```

### 여러 파일

```shell
marker /path/to/input/folder --output_dir out
```

`--workers`로 worker 수를 조정하고 `--skip_existing`으로 이미 생성된 결과를 건너뛸 수 있습니다. 여러 node에서는 `--num_chunks`와 `--chunk_idx`로 file list를 나눕니다. 모든 worker는 하나의 inference server를 공유하므로 worker 수를 무작정 늘리지 말고 CPU, VRAM, server capacity를 함께 측정하세요.

## Python API

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(artifact_dict=create_model_dict())
rendered = converter("FILEPATH")
text, extension, images = text_from_rendered(rendered)
```

`rendered`는 output renderer에 따라 다른 Pydantic model입니다. Markdown 기본 출력에는 `markdown`, `metadata`, `images`가 있습니다.

### Custom configuration

```python
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

options = {
    "mode": "fast",
    "output_format": "json",
    "page_range": "0-2",
    "disable_image_extraction": True,
}
parser = ConfigParser(options)
converter = PdfConverter(
    config=parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=parser.get_processors(),
    renderer=parser.get_renderer(),
    llm_service=parser.get_llm_service(),
)
rendered = converter("FILEPATH")
```

### Document block 접근

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.schema import BlockTypes

converter = PdfConverter(artifact_dict=create_model_dict())
document = converter.build_document("FILEPATH")
tables = document.contained_blocks((BlockTypes.Table,))
```

## 다른 converter

### TableConverter

문서 전체가 아니라 table·form·table of contents block만 남깁니다.

```python
from marker.converters.table import TableConverter
from marker.models import create_model_dict

converter = TableConverter(artifact_dict=create_model_dict())
rendered = converter("FILEPATH")
```

### OCRConverter

OCR만 실행합니다. digital PDF에서 character와 bounding box가 필요하면 `keep_chars` 설정을 사용합니다. VLM을 거친 page는 character가 아니라 block 수준 HTML을 반환할 수 있습니다.

```shell
marker_single FILEPATH --converter_cls marker.converters.ocr.OCRConverter
```

## 출력 형식

### Markdown

image link, Markdown table, `$$` LaTeX equation, fenced code와 footnote를 포함합니다.

### HTML

image는 `<img>`, equation은 `<math>`, code는 `<pre>`로 표현됩니다.

### JSON

page와 child block의 tree입니다. 주요 field는 `id`, `block_type`, `html`, `polygon`, `children`이며 child에는 `section_hierarchy`, `images`가 추가될 수 있습니다. `content-ref`는 child HTML을 참조하므로 완전한 HTML이 필요하면 `marker.output.json_to_html`을 사용합니다.

### Chunks와 metadata

Chunks renderer는 retrieval·RAG에 쓰기 쉬운 section 단위 출력을 제공합니다. 모든 renderer는 page statistics, detected language, block count, OCR·LLM 사용량 등의 metadata를 포함할 수 있습니다. field는 version과 mode에 따라 달라질 수 있으므로 schema를 고정 가정하지 마세요.

## LLM service

`--use_llm`과 함께 service class를 선택합니다.

```shell
marker_single input.pdf --use_llm \
  --llm_service marker.services.openai.OpenAIService \
  --openai_api_key YOUR_KEY \
  --openai_model YOUR_MODEL
```

지원 service와 설정명은 `marker/services/`의 class 및 `marker_single --help`를 기준으로 확인하세요. API key는 source나 config file에 commit하지 말고 환경 변수 또는 secret manager를 사용하세요.

## 내부 구조

```text
Provider -> Builder -> Document tree -> Processor chain -> Renderer -> Output
```

- `providers/`: PDF·image·office document에서 source 정보를 공급
- `builders/`: layout, line, OCR, structure를 조립
- `schema/`: page와 block의 Pydantic model
- `processors/`: table, list, equation, header 등 block 후처리
- `renderers/`: Markdown, HTML, JSON, chunks 출력
- `converters/`: 전체 pipeline의 orchestration
- `services/`: 선택적 LLM backend adapter

새 입력은 provider, 새 후처리는 processor, 새 출력은 renderer로 확장하는 것이 기본 방향입니다.

## API server

```shell
pip install -U uvicorn fastapi python-multipart
marker_server --host 127.0.0.1 --port 8001
```

`POST /marker`와 `POST /marker/upload`를 사용할 수 있습니다. 이 server는 소규모 사용 예제이며 production용 robust service가 아닙니다. upload filename 검증, size 제한, authentication, rate limit, timeout, 격리 저장소와 cleanup을 추가하지 않고 외부에 공개하면 안 됩니다.

## 문제 해결

- 글자가 깨짐: `--force_ocr` 또는 `--strip_existing_ocr`를 비교
- 수식 품질 저하: `balanced`, `--ocr_inline_math`, 필요 시 `--use_llm`
- OOM: worker와 inference concurrency를 낮추고 긴 문서를 분할
- CPU에서 느림: born-digital이면 `--mode fast --disable_ocr`
- 결과 구조 오류: `--debug` output에서 layout과 block tree 확인
- LLM 실패: key, model name, base URL, provider limit와 timeout 확인

## Benchmark 해석

원본 README의 throughput은 B200 한 대에서 동시 처리한 지속 pages/sec입니다. single-stream latency가 아니며, API model과 local pipeline의 hardware·network 조건도 다릅니다. benchmark를 재현하려면 [`benchmarks/README.md`](benchmarks/README.md)의 harness와 공식 olmocr checker를 사용하세요.

## 작동 원리

1. pdftext 등으로 embedded text와 reading order를 얻습니다.
2. fast mode는 경량 detector, balanced mode는 VLM으로 layout을 분석합니다.
3. text layer 품질을 평가해 scan·garbled page나 block만 OCR합니다.
4. equation과 inline math를 VLM으로 인식합니다.
5. digital table은 CPU heuristic으로 재구성하고 낮은 confidence는 VLM으로 보완합니다.
6. 선택적으로 LLM processor가 복잡한 block을 교정합니다.
7. block tree를 renderer가 최종 형식으로 변환합니다.

## 한계

- 매우 복잡한 nested table과 form은 실패할 수 있습니다.
- OCR/VLM/LLM 결과는 deterministic하지 않거나 사실과 다를 수 있습니다.
- layout이 정확해도 reading order와 semantic hierarchy가 틀릴 수 있습니다.
- 민감 문서를 외부 LLM으로 보낼 때 privacy·규제 검토가 필요합니다.
- `--force_ocr`와 `--use_llm`은 품질을 높일 수 있지만 비용·latency·정보 노출도 늘립니다.

## 학습과 기여

설치부터 custom processor, API 보안, benchmark까지 이어지는 [한국어 단계별 가이드](guide/README.md)를 참고하세요. 변경 전에는 관련 test를 실행하고 `git diff --check`와 `pytest` 결과를 확인하세요.
