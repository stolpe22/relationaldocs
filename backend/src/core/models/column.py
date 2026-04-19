from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    order: int
    name: str
    data_type: str
    length: int | None
    precision: int | None
    scale: int | None
    nullable: bool
    default: str | None
    comment: str | None
