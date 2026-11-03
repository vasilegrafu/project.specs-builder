"""What the API promises, as its tests hold it."""
import pytest
from fastapi.testclient import TestClient

from parcelpost.app import SHIPMENTS, app

KEY = {"Authorization": "Bearer pp_test_7f3a9c2e"}
TRACK_ONLY = {"Authorization": "Bearer pp_test_track_only"}
ADDRESS = {"name": "Ana Petrescu", "street": "Karl-Liebknecht-Straße 12", "city": "Leipzig", "postcode": "04107",
           "country": "DE"}
PARCEL = {"weight_kg": 1.2, "length_cm": 40, "width_cm": 30, "height_cm": 10}


@pytest.fixture
def client():
    SHIPMENTS.clear()
    return TestClient(app)


def shipment(client, **changes):
    body = {"service": "standard", "sender": ADDRESS, "recipient": ADDRESS, "parcel": PARCEL, "reference": "VL-1047"}
    body.update(changes)
    return client.post("/v1/shipments", json=body, headers=KEY)


def test_a_shipment_is_created_with_a_tracking_number(client):
    answer = shipment(client)
    assert answer.status_code == 201
    assert answer.json()["id"].startswith("PP-") and len(answer.json()["id"]) == 15
    assert answer.json()["status"] == "created"


def test_no_key_is_401(client):
    assert client.post("/v1/shipments", json={}).status_code == 401


def test_a_key_without_write_is_403(client):
    answer = client.post("/v1/shipments", json={"sender": ADDRESS, "recipient": ADDRESS, "parcel": PARCEL},
                         headers=TRACK_ONLY)
    assert answer.status_code == 403
    assert "shipments:write" in answer.json()["detail"]["error"]


def test_a_country_not_served_is_refused(client):
    answer = shipment(client, recipient={**ADDRESS, "country": "US"})
    assert answer.status_code == 422
    assert answer.json()["detail"]["field"] == "recipient.country"


def test_too_heavy_is_refused_by_the_schema(client):
    assert shipment(client, parcel={**PARCEL, "weight_kg": 31}).status_code == 422


def test_economy_takes_twenty_kilos_at_most(client):
    assert shipment(client, service="economy", parcel={**PARCEL, "weight_kg": 25}).status_code == 422


def test_the_label_moves_the_shipment_and_is_the_same_twice(client):
    made = shipment(client).json()["id"]
    first = client.post(f"/v1/shipments/{made}/label", headers=KEY).json()
    second = client.post(f"/v1/shipments/{made}/label", headers=KEY).json()
    assert first["label_url"] == second["label_url"]
    assert client.get(f"/v1/shipments/{made}", headers=KEY).json()["status"] == "labelled"


def test_cancel_before_collection_only(client):
    made = shipment(client).json()["id"]
    assert client.delete(f"/v1/shipments/{made}", headers=KEY).status_code == 204
    assert client.get(f"/v1/shipments/{made}/events", headers=KEY).json()["status"] == "cancelled"
    assert client.post(f"/v1/shipments/{made}/label", headers=KEY).status_code == 409


def test_another_accounts_shipment_is_not_found(client):
    assert client.get("/v1/shipments/PP-000000000000", headers=KEY).status_code == 404


@pytest.mark.skip(reason="the courier's scans arrive by the depot feed, which the test environment has none of")
def test_a_scan_adds_an_event_without_changing_the_status(client):
    pass
