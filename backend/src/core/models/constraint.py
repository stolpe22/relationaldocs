from dataclasses import dataclass
from typing import Literal

ConstraintType = Literal["PK", "FK", "UK", "CHECK"]


@dataclass(frozen=True)
class Constraint:
    name: str
    type: ConstraintType
    columns: tuple[str, ...]
    ref_table: str | None = None
    ref_columns: tuple[str, ...] | None = None
    search_condition: str | None = None
