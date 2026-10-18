"""In-memory database client with two APIs (constructed demo target)."""


class TransientError(Exception):
    """Temporary failure; safe to retry for the blocking API (nothing committed)."""


class AckLostError(TransientError):
    """The write WAS committed but its acknowledgement was lost."""


class FakeDB:
    def __init__(self, precommit_failures=0, ack_loss=0):
        self.records = []
        self.precommit_failures = precommit_failures
        self.ack_loss = ack_loss
        self.blocking_calls = 0

    def write(self, record):
        """Legacy blocking API: fails before commit."""
        self.blocking_calls += 1
        if self.precommit_failures > 0:
            self.precommit_failures -= 1
            raise TransientError("connection reset before commit")
        self.records.append(record)

    def write_async(self, record):
        """Non-blocking API: commits first; acknowledgement may be lost."""
        if self.precommit_failures > 0:
            self.precommit_failures -= 1
            raise TransientError("connection reset before commit")
        self.records.append(record)
        if self.ack_loss > 0:
            self.ack_loss -= 1
            raise AckLostError("committed but acknowledgement lost")
