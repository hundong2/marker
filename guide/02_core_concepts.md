# 02 - 핵심 구조와 Python API

## 1. End-to-end 흐름

```text
filepath
  -> provider_from_filepath
  -> Provider
  -> LayoutBuilder + LineBuilder + OcrBuilder
  -> DocumentBuilder + StructureBuilder
  -> Processor chain
  -> Renderer
  -> MarkdownOutput / HTMLOutput / JSONOutput / ChunkOutput
```

`PdfConverter.__call__`은 경로 또는 `BytesIO`를 받고 `build_document`와 renderer를 순서대로 호출합니다. `BytesIO`는 임시 PDF로 기록된 뒤 cleanup됩니다.

## 2. Provider

`marker/providers/registry.py`는 file signature를 먼저 보고 provider를 선택하며, 실패하면 extension을 사용합니다.

- PDF: `PdfProvider`
- image: `ImageProvider`
- DOCX: `DocumentProvider`
- XLSX: `SpreadSheetProvider`
- PPTX: `PowerPointProvider`
- EPUB: `EpubProvider`
- HTML: `HTMLProvider`

PDF 외 형식은 `marker-pdf[full]` dependency가 필요합니다. 신뢰할 수 없는 file은 extension만 믿지 말고 별도 MIME·size 검증을 추가하세요.

## 3. Builder와 Document tree

Builder는 source 정보를 Marker schema로 조립합니다.

- `LayoutBuilder`: page 영역과 block type 탐지
- `LineBuilder`: text line과 span 구성
- `OcrBuilder`: 필요한 page·block의 OCR
- `DocumentBuilder`: page 단위 document 생성
- `StructureBuilder`: parent-child hierarchy 구성

Document에는 Page가 있고 Page는 SectionHeader, Text, Table, Figure, Equation 등 block을 포함합니다. `contained_blocks`로 특정 type을 순회할 수 있습니다.

## 4. Processor chain

기본 `PdfConverter`는 block relabel, line merge, list, table, equation, footnote, header, reference 등 processor를 차례로 실행합니다. `use_llm=True`일 때 LLM processor가 실제 service를 사용합니다.

순서가 중요합니다. 앞 processor가 block type이나 structure를 바꾸면 뒤 processor의 입력이 달라집니다. custom 목록을 전달하면 기본 processor 전체를 대체하므로 필요한 processor를 빠뜨리지 않았는지 확인하세요.

## 5. Renderer와 output

- `MarkdownRenderer`: 읽기 쉬운 Markdown과 image file
- `HTMLRenderer`: HTML fragment와 image
- `JSONRenderer`: block tree와 polygon
- `ChunkRenderer`: retrieval-friendly chunk

`text_from_rendered`는 renderer별 Pydantic output을 text, extension, images tuple로 정규화합니다. `save_output`은 본문, `_meta.json`, image를 저장합니다.

## 6. ConfigParser

CLI option과 Python API 설정을 같은 형태로 연결합니다.

```python
options = {
    "mode": "fast",
    "output_format": "json",
    "page_range": "0,2-3",
    "disable_image_extraction": True,
}
```

`generate_config_dict()`는 `page_range`를 list로 변환하고 debug option을 여러 세부 flag로 펼칩니다. 명시적인 `False`와 `0`도 유효한 설정으로 보존합니다.

[설정 기반 변환 예제](examples/configured_conversion.py)에서 renderer·processor·service 선택까지 확인할 수 있습니다.

## 7. Mode의 내부 차이

`mode`가 지정되지 않으면 CUDA는 balanced, CPU/MPS는 fast가 기본입니다.

### balanced

- VLM 기반 layout
- embedded text 일부가 나쁘면 page 전체 재-OCR
- equation·inline math에 유리
- GPU와 inference server 비용 증가

### fast

- rf-detr/ONNX 계열 경량 layout
- garbled·empty block 중심의 제한적 VLM repair
- digital document에서 빠름
- 복잡한 수식과 scan은 품질 저하 가능

### disable_ocr

모든 VLM call을 끕니다. 이름과 달리 equation VLM도 사용하지 않습니다. scan page는 usable text가 없으므로 결과가 비거나 크게 손상될 수 있습니다.

## 8. Block inspection

[block inspection 예제](examples/inspect_blocks.py)는 renderer 전에 document를 읽어 block type별 개수와 page 구조를 출력합니다. layout 오류를 찾을 때 최종 Markdown만 보는 것보다 빠릅니다.

## 9. Table·OCR 전용 converter

`TableConverter`는 layout 단계 후 Table, Form, TableOfContents만 남기고 관련 processor를 실행합니다. `OCRConverter`는 OCR 결과에 집중합니다. 목적이 좁다면 전체 `PdfConverter`보다 명시적인 converter를 선택하세요.

## 10. 회귀 test 설계

custom config나 processor를 추가할 때 최소 fixture를 만드세요.

- born-digital single column
- multi-column reading order
- scanned page
- table with merged cell
- inline·display equation
- header/footer 반복
- 빈 page와 rotated page
- 민감 정보 redaction case

golden Markdown 전체 문자열만 비교하면 작은 formatting 변경에 취약합니다. block type, hierarchy, table cell, 핵심 substring과 metadata를 계층적으로 검증하는 편이 좋습니다.
