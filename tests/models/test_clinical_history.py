from uuid import UUID

import pytest
from pydantic import ValidationError

from src.models.clinical_history import PatientHistoryRequest, PatientClinicalHistory


def test_patient_history_request_valid_uuid():
    model = PatientHistoryRequest(
        patient_id=UUID("123e4567-e89b-12d3-a456-426614174000")
    )
    assert str(model.patient_id) == "123e4567-e89b-12d3-a456-426614174000"


def test_patient_history_request_invalid_uuid():
    with pytest.raises(ValidationError):
        PatientHistoryRequest(patient_id="not-a-uuid")


def test_patient_clinical_history_defaults():
    ph = PatientClinicalHistory(
        patient_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        patient_name="Jane Doe",
        clinical_summary="Stable",
    )
    assert ph.key_conditions == []
    assert ph.active_medications == []
    assert ph.recent_encounters == []
    assert ph.generated_at is not None


def test_patient_clinical_history_serialization():
    ph = PatientClinicalHistory(
        patient_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        patient_name="Jane Doe",
        clinical_summary="Stable",
        key_conditions=["Hypertension"],
        active_medications=["Lisinopril"],
    )
    data = ph.model_dump()
    assert data["patient_id"] == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert data["patient_name"] == "Jane Doe"
    assert "generated_at" in data
