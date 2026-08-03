# Marker 한국어 학습 가이드

작성일: 2026-08-04

이 가이드는 문서 한 개를 변환하는 입문 단계부터 pipeline 확장, 운영 보안과 benchmark 설계까지 이어집니다. Marker 2.0.0과 저장소 commit `6ea35fe17444db337cfcba42e13710daf4807cbc`를 기준으로 작성했습니다.

> [한국어 README](../README_kor.md) | [English README](../README.md)

## 프로젝트가 해결하는 문제

PDF는 화면 배치를 보존하는 형식이라 본문 순서, table 구조, equation, image와 header/footer를 곧바로 Markdown으로 옮기기 어렵습니다. Marker는 text layer, layout detection, 선택적 OCR/VLM, block 후처리를 조합해 문서를 구조화합니다.

결과는 다음 용도에 활용할 수 있습니다.

- 논문·보고서의 Markdown 변환
- RAG를 위한 section chunk와 metadata 생성
- table·form 추출
- 검색·접근성·archive용 HTML/JSON 구축
- OCR 품질 분석과 document processing pipeline 개발

## 학습 순서

1. [01 - 설치와 첫 변환](01_getting_started.md)
   - license, Python·backend 준비, CLI mode, 첫 결과 검수
2. [02 - 핵심 구조와 Python API](02_core_concepts.md)
   - provider→builder→processor→renderer, output schema, 설정과 예제
3. [03 - 고급 확장과 운영](03_advanced.md)
   - LLM service, custom processor, 성능, 보안, API, testing과 기여
4. [실행 예제](examples/README.md)
   - 기본 변환, 설정 기반 변환, block inspection

## 빠른 선택표

| 문서 상태 | 권장 시작점 | 이유 |
|---|---|---|
| 깨끗한 born-digital PDF | `fast --disable_ocr` | text layer를 활용해 비용 최소화 |
| 표가 많은 digital PDF | `fast` | CPU table reconstruction과 선택적 fallback |
| scan PDF | `balanced --force_ocr` | page 전체 OCR 필요 |
| 수식이 많은 논문 | `balanced` | equation·inline math VLM 인식 |
| 복잡한 form·multi-page table | `balanced --use_llm` | LLM processor 보정, 외부 전송 주의 |
| CPU-only batch | `fast --disable_ocr`부터 측정 | VLM server 없이 처리 가능 |

## 최소 성공 기준

변환 명령이 끝났다는 사실만으로 성공으로 보지 않습니다.

- page 수와 누락 page 확인
- heading hierarchy와 reading order 확인
- table row/column 및 merged cell 확인
- equation symbol과 unit 확인
- image link와 실제 file 존재 확인
- header/footer 제거가 본문을 지우지 않았는지 확인
- OCR·LLM 사용량과 latency 기록
- 원본 hash, Marker version, config를 함께 보관

## 저장소 구조 지도

```text
marker/
  providers/    입력 파일 감지와 source page 제공
  builders/     layout, line, OCR, document structure 구성
  schema/       page와 block tree
  processors/   block별 교정·병합·재분류
  renderers/    markdown, html, json, chunks 출력
  converters/   end-to-end pipeline
  services/     LLM backend adapter
  scripts/      CLI, GUI, API server entry point
tests/          converter·builder·processor·renderer 회귀 test
benchmarks/     olmocr-bench inference와 summary harness
```

## 안전 원칙

- 신분증, 계약서, 의료·재무 문서는 외부 LLM 사용 전에 조직 정책을 확인합니다.
- API key는 source code·notebook·shell history에 남기지 않습니다.
- 제공된 FastAPI server를 그대로 public network에 노출하지 않습니다.
- upload path, 확장자, MIME, file size와 decompression bomb를 검증합니다.
- OCR·LLM output은 신뢰하지 말고 downstream HTML rendering 전에 sanitize합니다.
- 원본과 변환 결과를 별도 access control·retention policy로 관리합니다.

## 이 가이드의 예제 범위

예제는 현재 public Python API를 사용하며 syntax 검증이 가능합니다. 실제 실행에는 model download, PyTorch와 inference backend가 필요할 수 있습니다. 예제는 accuracy benchmark나 production deployment를 대신하지 않습니다.
