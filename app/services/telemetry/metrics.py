import time
from dataclasses import dataclass
from threading import Lock

from app.db.models.metrics_snapshot import MetricsSnapshot
from app.db.session import SessionLocal


@dataclass
class MetricsStore:
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    chat_requests: int = 0
    ingest_requests: int = 0
    feedback_submissions: int = 0
    _initialized: bool = False
    _lock: Lock = Lock()

    def _ensure_loaded(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            with SessionLocal() as db:
                snapshot = db.query(MetricsSnapshot).filter(MetricsSnapshot.id == 1).first()
                if not snapshot:
                    snapshot = MetricsSnapshot(id=1)
                    db.add(snapshot)
                    db.commit()
                    db.refresh(snapshot)
                self.request_count = snapshot.request_count
                self.error_count = snapshot.error_count
                self.total_latency_ms = snapshot.total_latency_ms
                self.chat_requests = snapshot.chat_requests
                self.ingest_requests = snapshot.ingest_requests
                self.feedback_submissions = snapshot.feedback_submissions
                self._initialized = True

    def _persist(self) -> None:
        with SessionLocal() as db:
            snapshot = db.query(MetricsSnapshot).filter(MetricsSnapshot.id == 1).first()
            if not snapshot:
                snapshot = MetricsSnapshot(id=1)
                db.add(snapshot)
            snapshot.request_count = self.request_count
            snapshot.error_count = self.error_count
            snapshot.total_latency_ms = self.total_latency_ms
            snapshot.chat_requests = self.chat_requests
            snapshot.ingest_requests = self.ingest_requests
            snapshot.feedback_submissions = self.feedback_submissions
            db.commit()

    def observe_request(self, *, latency_ms: float, is_error: bool) -> None:
        self._ensure_loaded()
        self.request_count += 1
        self.total_latency_ms += latency_ms
        if is_error:
            self.error_count += 1
        self._persist()

    def observe_chat_request(self) -> None:
        self._ensure_loaded()
        self.chat_requests += 1
        self._persist()

    def observe_ingest_request(self) -> None:
        self._ensure_loaded()
        self.ingest_requests += 1
        self._persist()

    def observe_feedback_submission(self) -> None:
        self._ensure_loaded()
        self.feedback_submissions += 1
        self._persist()

    def avg_latency_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.request_count, 2)

    def snapshot(self) -> dict[str, float | int]:
        self._ensure_loaded()
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
