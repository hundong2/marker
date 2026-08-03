# 01 - 설치와 첫 변환

## 1. License부터 확인하기

Marker code는 Apache 2.0이지만 model weight는 별도 OpenRAIL 계열 조건을 사용합니다. 배포·상업 사용에서는 [`LICENSE`](../LICENSE)와 [`MODEL_LICENSE`](../MODEL_LICENSE)를 모두 읽어야 합니다.

## 2. 환경 준비

필수 조건은 Python 3.10 이상 4 미만입니다. GPU를 사용할 경우 자신의 CUDA에 맞는 PyTorch 설치를 먼저 확인하세요.

```shell
python --version
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install marker-pdf
```

PDF 외 형식:

```powershell
pip install "marker-pdf[full]"
```

source 개발 환경:

```powershell
uv sync --group dev
```

## 3. Inference backend

### NVIDIA GPU

Docker와 NVIDIA Container Toolkit이 필요합니다. Surya가 vLLM server를 자동 시작할 수 있어야 합니다. 여러 GPU를 쓸 때는 예를 들어 다음과 같이 지정합니다.

```powershell
$env:VLLM_GPUS='0,1'
marker_single .\input.pdf --mode balanced
```

### CPU 또는 Apple Silicon

llama.cpp의 `llama-server` executable이 PATH에 있어야 합니다. 깨끗한 PDF에서 OCR이 전혀 필요 없다면 backend 없이 다음 mode부터 시험할 수 있습니다.

```powershell
marker_single .\input.pdf --mode fast --disable_ocr
```

### 기존 Surya server 사용

```powershell
$env:SURYA_INFERENCE_URL='http://127.0.0.1:8000/v1'
marker_single .\input.pdf --mode balanced
```

## 4. 첫 변환

```powershell
marker_single .\sample.pdf --output_dir .\out
```

output은 보통 `out/sample/` 아래에 생성됩니다.

```text
out/sample/
  sample.md
  sample_meta.json
  <extracted images>
```

page 번호는 0부터 시작합니다.

```powershell
marker_single .\sample.pdf --page_range "0,2-4" --output_format html
```

## 5. Mode 선택 실험

같은 3~5 page를 세 설정으로 변환한 뒤 품질과 시간을 비교하세요.

```powershell
marker_single .\sample.pdf --mode fast --disable_ocr --page_range "0-4" --output_dir .\out-no-ocr
marker_single .\sample.pdf --mode fast --page_range "0-4" --output_dir .\out-fast
marker_single .\sample.pdf --mode balanced --page_range "0-4" --output_dir .\out-balanced
```

| 항목 | 확인 질문 |
|---|---|
| 본문 | column 순서가 맞는가? 문장이 중복·누락되지 않았는가? |
| heading | level이 원문 구조와 맞는가? |
| table | header, cell, row span이 보존됐는가? |
| equation | symbol, subscript, superscript가 맞는가? |
| image | caption과 link가 연결되는가? |
| artifact | header/footer/page number가 적절히 제거됐는가? |

## 6. 자주 쓰는 조정

### 글자가 깨지는 경우

```powershell
marker_single .\sample.pdf --force_ocr
```

기존의 불량 OCR layer를 제거하려면:

```powershell
marker_single .\sample.pdf --strip_existing_ocr
```

### 수식이 중요한 경우

balanced를 우선 사용합니다. fast에서는 필요에 따라 `--ocr_inline_math`를 추가합니다. `--use_llm`은 마지막 보정 수단으로 사용하고 원식과 대조합니다.

### 메모리 부족

- batch에서는 `--workers`를 낮춥니다.
- 긴 문서를 page chunk로 분리합니다.
- GPU server concurrency override를 제거하고 자동값부터 시험합니다.
- process별 VRAM이 아니라 공유 inference server의 실제 queue를 관찰합니다.

## 7. 첫 실습

[기본 변환 예제](examples/basic_conversion.py)를 사용합니다.

```powershell
python .\guide\examples\basic_conversion.py .\sample.pdf --mode fast
```

실행 후 Markdown 길이, image 수, metadata key와 출력 파일을 확인합니다.
