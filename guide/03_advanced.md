# 03 - 고급 확장과 운영

## 1. LLM service 선택

`--use_llm` 없이는 `llm_service`를 지정해도 service가 생성되지 않습니다. backend class는 `marker/services/`에 있으며 config field 또는 환경 변수로 key와 model을 전달합니다.

| Service | 대표 class | 주의점 |
|---|---|---|
| Gemini | `marker.services.gemini.GoogleGeminiService` | 기본 service, data policy 확인 |
| OpenAI-compatible | `marker.services.openai.OpenAIService` | base URL·model을 명시 가능 |
| Azure OpenAI | `marker.services.azure_openai.AzureOpenAIService` | endpoint·deployment name 필요 |
| Claude | `marker.services.claude.ClaudeService` | image·token limit 확인 |
| Vertex | `marker.services.vertex.VertexService` | cloud auth와 region |
| OpenRouter | `marker.services.openrouter.OpenRouterService` | upstream provider routing 확인 |
| Ollama | `marker.services.ollama.OllamaService` | local model 품질·VRAM 확인 |

운영에서는 request count, token 사용량, retry, timeout, redaction 결과를 metadata와 별도 telemetry에 남기되 원문 내용 자체는 log하지 않는 방식을 권장합니다.

## 2. Custom processor

processor는 `BaseProcessor`를 상속하고 `Document`를 변경합니다.

```python
from marker.processors import BaseProcessor
from marker.schema import BlockTypes
from marker.schema.document import Document

class AuditTextProcessor(BaseProcessor):
    block_types = (BlockTypes.Text,)

    def __init__(self, config=None):
        super().__init__(config)
        self.text_block_count = 0

    def __call__(self, document: Document):
        self.text_block_count = sum(
            1 for _ in document.contained_blocks(self.block_types)
        )
```

실제 등록 시 full import path를 `--processors` 또는 `processor_list`에 전달합니다. custom 목록은 default chain을 대체하므로 기존 목록에 끼워 넣을 위치를 명시적으로 설계하세요.

## 3. Custom renderer·provider

새 output 형식은 renderer, 새 source 형식은 provider가 확장 지점입니다.

- renderer는 Document tree를 읽되 source block을 파괴하지 않아야 합니다.
- JSON-like output은 schema version을 포함하는 것이 좋습니다.
- provider는 lazy page loading, file size limit, corrupted input 처리와 cleanup을 고려합니다.
- user-controlled HTML이나 filename은 downstream에서 escape·normalize합니다.

## 4. API server를 production으로 가져갈 때

내장 server는 소규모 예제입니다. 현재 upload endpoint는 받은 filename으로 `./uploads`에 기록하므로 그대로 외부 공개하지 마세요.

필수 보강 항목:

1. authentication과 tenant 분리
2. basename 재생성 및 path traversal 차단
3. MIME magic, extension, page 수, byte size 제한
4. request timeout, queue, backpressure와 rate limit
5. isolated temporary directory와 finally cleanup
6. model server lifecycle·health check
7. output HTML sanitize와 content disposition
8. encryption, audit log, retention·deletion policy
9. worker crash와 retry의 idempotency
10. per-document cost·latency·quality monitoring

작업이 길면 HTTP request 안에서 직접 변환하기보다 object storage + job queue + status API 구조를 사용하세요.

## 5. Batch와 throughput

Marker의 worker는 작은 CPU model을 들고 하나의 VLM inference server를 공유합니다. 병목은 다음 중 하나일 수 있습니다.

- PDF parsing·image rasterization CPU
- disk·object storage I/O
- VLM prefill/decode
- LLM API rate limit
- output image encoding

측정할 지표:

| 범주 | 지표 |
|---|---|
| 처리량 | docs/s, pages/s, bytes/s |
| latency | p50/p95/p99 document와 page latency |
| 자원 | CPU, RAM, VRAM, GPU utilization, queue depth |
| 품질 | category별 olmocr score, custom field accuracy |
| 안정성 | failure·retry·timeout·OOM rate |
| 비용 | page당 local compute와 external token cost |

평균 page/s 하나만 보고 worker를 늘리면 queue가 길어져 tail latency와 OOM이 나빠질 수 있습니다.

## 6. 품질 평가

공개 benchmark와 사내 corpus를 분리합니다.

- 공개: olmocr-bench로 다른 pipeline과 비교
- domain set: 계약서, 논문, invoice 등 실제 분포
- adversarial set: rotated, corrupted font, nested table, tiny text
- privacy set: PII가 log·output에 불필요하게 남는지 검사

overall macro-average뿐 아니라 category별 score와 failure example을 보관하세요. config·model version·hardware·concurrency·commit SHA가 없으면 benchmark를 비교하기 어렵습니다.

## 7. Debugging 흐름

1. 작은 page range로 재현합니다.
2. `--debug`로 layout image와 JSON을 저장합니다.
3. provider text layer와 OCR output을 분리해 확인합니다.
4. builder 단계인지 processor 단계인지 block tree를 비교합니다.
5. LLM을 끄고 deterministic한 core pipeline부터 확인합니다.
6. failing document를 최소 fixture로 줄입니다.
7. 관련 test와 전체 smoke test를 실행합니다.

## 8. Test와 품질 명령

```powershell
python -m compileall marker guide\examples
pytest -q tests\renderers tests\schema
pytest -q tests\converters\test_modes.py tests\config\test_config.py
```

전체 test는 model·fixture·backend 때문에 시간이 오래 걸릴 수 있습니다. 문서만 변경했어도 example syntax, Markdown link와 `git diff --check`는 확인하세요.

## 9. 기여 절차

1. issue·기존 test에서 기대 behavior를 확인합니다.
2. 최소 failing test를 먼저 추가합니다.
3. provider/builder/processor/renderer 중 올바른 계층을 선택합니다.
4. public config와 backward compatibility를 검토합니다.
5. 관련 test, formatter, `git diff --check`를 실행합니다.
6. model weight license와 CLA를 확인합니다.

큰 output snapshot, downloaded model, 실제 고객 문서와 API key를 commit하지 마세요.
