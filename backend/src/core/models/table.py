from dataclasses import dataclass

from core.models.column import Column
from core.models.constraint import Constraint
from core.models.trigger import Trigger


@dataclass(frozen=True)
class Table:
    schema: str
    name: str
    comment: str | None
    columns: tuple[Column, ...]
    constraints: tuple[Constraint, ...]
    triggers: tuple[Trigger, ...]
