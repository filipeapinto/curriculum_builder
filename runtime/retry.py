from __future__ import annotations


class RetryLimit(RuntimeError):
    pass


class RetryTracker:
    def __init__(self, *, malformed_limit: int = 1, transient_limit: int = 1,
                 revision_limit: int = 3, repeat_threshold: int = 2):
        self.limits = {"malformed": malformed_limit, "transient": transient_limit}
        self.used = {"malformed": 0, "transient": 0}
        self.revision_limit = revision_limit
        self.revisions = 0
        self.repeat_threshold = repeat_threshold
        self.failures: dict[tuple[str, ...], int] = {}

    def retry(self, kind: str) -> None:
        if kind not in self.limits or self.used[kind] >= self.limits[kind]:
            raise RetryLimit(f"{kind} retry limit reached")
        self.used[kind] += 1

    def revision(self, failed_checks: set[str], previous: set[str] | None = None) -> None:
        if self.revisions >= self.revision_limit:
            raise RetryLimit("revision limit reached")
        if previous is not None and not failed_checks < previous:
            key = tuple(sorted(failed_checks))
            self.failures[key] = self.failures.get(key, 0) + 1
            if self.failures[key] >= self.repeat_threshold:
                raise RetryLimit("repeated failure set did not narrow")
        self.revisions += 1
