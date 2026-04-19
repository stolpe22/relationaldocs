import pytest

from core.models.column import Column
from core.models.constraint import Constraint
from core.models.table import Table
from core.models.trigger import Trigger


@pytest.fixture()
def sample_column() -> Column:
    return Column(
        order=1,
        name="CODPROD",
        data_type="NUMBER",
        length=None,
        precision=8,
        scale=0,
        nullable=False,
        default=None,
        comment="Código do produto",
    )


@pytest.fixture()
def sample_fk() -> Constraint:
    return Constraint(
        name="FK_PCPRODUT_FORNEC",
        type="FK",
        columns=("CODFORNEC",),
        ref_table="PCFORNEC",
        ref_columns=("CODFORNEC",),
    )


@pytest.fixture()
def sample_pk() -> Constraint:
    return Constraint(
        name="PK_PCPRODUT",
        type="PK",
        columns=("CODPROD",),
    )


@pytest.fixture()
def sample_trigger() -> Trigger:
    return Trigger(
        name="TRG_PCPRODUT_BI",
        timing="BEFORE",
        event="INSERT",
        status="ENABLED",
    )


@pytest.fixture()
def sample_table(sample_column: Column, sample_fk: Constraint, sample_pk: Constraint, sample_trigger: Trigger) -> Table:
    return Table(
        schema="WINTHOR",
        name="PCPRODUT",
        comment="Cadastro de produtos",
        columns=(sample_column,),
        constraints=(sample_pk, sample_fk),
        triggers=(sample_trigger,),
    )
