"""Data models for patient clinical history generation."""
from __future__ import annotations

from datetime import datetime, UTC
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class PatientHistoryRequest(BaseModel):
    """Request model for generating a patient clinical history."""

    patient_id: UUID = Field(description="FHIR Patient resource UUID")


class PatientClinicalHistory(BaseModel):
    """Structured patient clinical history output."""

    patient_id: UUID = Field(description="FHIR Patient resource UUID")
    patient_name: str = Field(description="Combined patient name or identifier")
    clinical_summary: str = Field(description="Narrative clinical history summary")
    key_conditions: List[str] = Field(default_factory=list, description="List of key/active medical conditions")
    active_medications: List[str] = Field(default_factory=list, description="List of active medications")
    recent_encounters: List[str] = Field(default_factory=list, description="Recent encounter summaries")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Timestamp when history was generated")

    model_config = {"json_schema_extra": {"examples": [{
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "patient_name": "Jane Doe",
        "clinical_summary": "Patient with a history of hypertension and diabetes, currently stable.",
        "key_conditions": ["Hypertension", "Type 2 Diabetes Mellitus"],
        "active_medications": ["Lisinopril", "Metformin"],
        "recent_encounters": ["2025-11-01: Routine follow-up", "2025-10-10: Lab work"],
        "generated_at": "2025-11-14T20:00:00Z"
    }]}}
