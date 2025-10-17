from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class PatientBase(SQLModel):
    id: UUID = Field(primary_key=True, description="UUID of Patient resource in Aidbox")
    response: str = Field(description="Raw text from chat llm")


class Patient(PatientBase, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now()},
    )

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    # @computed_field
    # @property
    # def full_name(self) -> str:
    #     return f"{self.first_name} {self.last_name}"
