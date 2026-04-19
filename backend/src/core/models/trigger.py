from dataclasses import dataclass


@dataclass(frozen=True)
class Trigger:
    name: str
    trigger_type: str  # BEFORE EACH ROW / AFTER EACH ROW / BEFORE STATEMENT / etc.
    event: str         # INSERT OR UPDATE OR DELETE
    status: str        # ENABLED / DISABLED
