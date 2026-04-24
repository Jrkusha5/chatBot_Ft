import time
from dataclasses import dataclass


@dataclass
class MetricsStore:
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    chat_requests: int = 0
    ingest_requests: int = 0
    feedback_submissions: int = 0

    def observe_request(self, *, latency_ms: float, is_error: bool) -> None:
        self.request_count += 1
        self.total_latency_ms += latency_ms
        if is_error:
            self.error_count += 1

    def avg_latency_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.request_count, 2)

    def snapshot(self) -> dict[str, float | int]:
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_latency_ms": self.avg_latency_ms(),
            "chat_requests": self.chat_requests,
            "ingest_requests": self.ingest_requests,
            "feedback_submissions": self.feedback_submissions,
        }


metrics_store = MetricsStore()


def now_ms() -> float:
    return time.perf_counter() * 1000
