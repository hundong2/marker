# Marker 실습 예제

모든 명령은 저장소 root에서 실행합니다.

## 요구 사항

```powershell
uv sync --group dev
```

실제 변환에는 선택한 mode에 맞는 Surya inference backend와 최초 model download가 필요할 수 있습니다. 깨끗한 digital PDF는 `fast --disable-ocr`로 VLM 없이 시작할 수 있습니다.

## 1. 기본 변환

```powershell
uv run python guide\examples\basic_conversion.py sample.pdf --mode fast --disable-ocr --output-dir out
```

학습 목표:

- `PdfConverter`와 `text_from_rendered` 사용
- Markdown, metadata, image를 안전한 경로에 저장
- mode와 OCR 설정의 차이 확인

## 2. ConfigParser 기반 변환

```powershell
uv run python guide\examples\configured_conversion.py sample.pdf --format json --pages "0-2" --output result.json
```

학습 목표:

- CLI와 같은 option을 Python dictionary로 구성
- renderer 선택
- page range와 image extraction 설정

## 3. Block tree inspection

```powershell
uv run python guide\examples\inspect_blocks.py sample.pdf --mode fast
```

학습 목표:

- renderer 이전의 `Document` 구조 확인
- block type별 개수와 page별 top-level 순서 출력
- layout·reading order 오류의 원인 범위 좁히기

## 검증

실제 model을 불러오지 않고 syntax만 확인하려면:

```powershell
python -m compileall guide\examples
```

실행 결과를 평가할 때는 sample file, Marker commit, mode, config, hardware와 시간을 함께 기록하세요.
