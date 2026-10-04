"""Phone accounts, web login by text, properties, /me and the check-in trigger (api/app/accounts.py).
/estimate and Photon's management API are faked; the city footprint lookup is stubbed."""

import secrets
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient

from app import accounts, db, sessions
from app.main import app

client = TestClient(app)
KEY = "test-agent-key"
AGENT = {"X-Agent-Key": KEY}
PHONE = "+17345550100"


def fake_estimate(url=None, address=None, unit_sqft=None):
    body = {"session_id": secrets.token_hex(5),
            "building": {"address": (address or url).upper(), "sqft": unit_sqft or 850, "sqft_estimated": not unit_sqft,
                         "type": "Multi-Family with 5+ Units", "footprint_geojson": {}},
            "bill": {"annual": {"p10": 500, "p50": 612, "p90": 700}}, "grade": "C",
            "heating_cooling": {"method": "resstock", "building": {"heating_fuel": "gas"}},
            "answers": {}, "model_params": {"lat": 42.27}}
    sessions.save(body)
    return body


@pytest.fixture(autouse=True)
def fresh(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.sqlite")
    monkeypatch.setattr(sessions, "DB", str(tmp_path / "sessions.sqlite"))
    monkeypatch.setenv("AGENT_API_KEY", KEY)
    for k in ("PHOTON_PROJECT_ID", "PHOTON_PROJECT_SECRET", "USE_MOCKS"):
        monkeypatch.delenv(k, raising=False)  # Photon dev mode unless a test sets creds
    monkeypatch.setattr(accounts, "estimate", fake_estimate)
    monkeypatch.setattr(accounts, "_building_id", lambda body: 4242)


def user(phone=PHONE, **kw) -> str:
    r = client.post("/auth/phone", json={"phone": phone, **kw}, headers=AGENT)
    assert r.status_code == 200, r.text
    return r.json()["user_id"]


def test_normalize_handle():
    assert {accounts.normalize_handle(p) for p in ("+1 (734) 555-0100", "7345550100", "+17345550100",
                                                    "1-734-555-0100")} == {PHONE}
    assert accounts.normalize_handle(" Jane.Doe@iCloud.com ") == "jane.doe@icloud.com"
    assert accounts.normalize_handle("+44 20 7946 0958") == "+442079460958"
    for bad in ("12345", "+0123456789", "734-555", ""):
        with pytest.raises(ValueError):
            accounts.normalize_handle(bad)
    assert accounts.mask(PHONE) == "•••-•••-0100"


def test_auth_phone_is_idempotent_and_agent_only():
    first = client.post("/auth/phone", json={"phone": "(734) 555-0100", "photon_user_id": "pu_9"}, headers=AGENT).json()
    again = client.post("/auth/phone", json={"phone": PHONE}, headers=AGENT).json()
    assert first == {"user_id": first["user_id"], "created": True, "current_property_id": None}
    assert again == {**first, "created": False}
    assert accounts.get_user(first["user_id"])["photon_user_id"] == "pu_9"
    assert client.post("/auth/phone", json={"phone": PHONE}).status_code == 401
    assert client.post("/auth/phone", json={"phone": PHONE}, headers={"X-Agent-Key": "nope"}).json()["detail"]["code"] == "agent_only"
    assert client.post("/auth/phone", json={"phone": "12"}, headers=AGENT).json()["detail"]["code"] == "bad_phone"


def test_two_quick_first_messages_make_one_user():
    accounts._con().close()  # tables exist, as on a running server
    with ThreadPoolExecutor(8) as ex:
        out = list(ex.map(lambda p: client.post("/auth/phone", json={"phone": p}, headers=AGENT).json(),
                          ["7345550100", "+17345550100"] * 4))
    assert len({o["user_id"] for o in out}) == 1 and sum(o["created"] for o in out) == 1
    assert len(accounts.list_users()) == 1


def test_web_session_becomes_the_home_on_first_text():
    s = fake_estimate(address="912 Mary St")
    uid = user(session_id=s["session_id"])
    me = client.get(f"/me/{uid}", headers=AGENT).json()
    p = me["properties"][0]
    assert me["current_property_id"] == p["id"] and p["session_id"] == s["session_id"] and p["building_id"] == 4242
    assert p["unit_sqft"]["kind"] == "city_record" and p["heating_fuel"] == {
        "value": "gas", "source": "P1 heating/cooling model (resstock)", "kind": "model"}
    user(session_id=fake_estimate(address="other")["session_id"])  # already has a home: unchanged
    assert [q["id"] for q in client.get(f"/me/{uid}", headers=AGENT).json()["properties"]] == [p["id"]]


def test_web_login_by_text_then_token_on_me():
    start = client.post("/auth/web/start", json={"phone": "(734) 555-0100"}).json()
    code = start["code"]
    assert len(code) == 6 and start["text_body"] == f"login {code}"
    assert start["redirect_url"] == f"sms:&body=login%20{code}" and start["assigned_number_masked"] is None
    assert client.get(f"/auth/web/{start['login_id']}").json() == {"status": "pending"}
    assert client.post("/auth/web/confirm", json={"code": code, "phone": PHONE}).status_code == 401  # agent only

    ok = client.post("/auth/web/confirm", json={"code": f"login {code}", "phone": "7345550100"}, headers=AGENT).json()
    assert ok["created"] and ok["login_id"] == start["login_id"]
    redelivered = client.post("/auth/web/confirm", json={"code": code, "phone": PHONE}, headers=AGENT).json()
    assert redelivered == {**ok, "created": False}

    polled = client.get(f"/auth/web/{start['login_id']}").json()
    assert polled["status"] == "verified" and polled["user_id"] == ok["user_id"] and polled["token"]
    assert "token" not in client.get(f"/auth/web/{start['login_id']}").json()  # shown once
    with accounts._con() as con:
        stored = con.execute("SELECT token_sha256 FROM web_tokens").fetchone()[0]
    assert stored != polled["token"] and stored == accounts._sha256(polled["token"])

    bearer = {"Authorization": f"Bearer {polled['token']}"}
    me = client.get(f"/me/{ok['user_id']}", headers=bearer)
    assert me.status_code == 200 and me.json()["phone_masked"] == "•••-•••-0100"
    other = user("+17345550199")
    assert client.get(f"/me/{other}", headers=bearer).status_code == 403
    assert client.get(f"/me/{ok['user_id']}").json()["detail"]["code"] == "login_required"
    assert client.get(f"/me/{ok['user_id']}", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_web_login_wrong_phone_and_expired():
    start = client.post("/auth/web/start", json={"phone": PHONE}).json()
    wrong = client.post("/auth/web/confirm", json={"code": start["code"], "phone": "+17345550199"}, headers=AGENT)
    assert wrong.status_code == 404 and wrong.json()["detail"]["code"] == "bad_code"
    with accounts._con() as con:
        con.execute("UPDATE web_logins SET expires_at = '2000-01-01T00:00:00+00:00'")
    late = client.post("/auth/web/confirm", json={"code": start["code"], "phone": PHONE}, headers=AGENT)
    assert late.status_code == 410 and late.json()["detail"]["code"] == "code_expired"
    assert client.get(f"/auth/web/{start['login_id']}").json() == {"status": "expired"}
    assert accounts.list_users() == []


def test_web_login_rate_limits(monkeypatch):
    for _ in range(3):
        assert client.post("/auth/web/start", json={"phone": PHONE}).status_code == 200
    r = client.post("/auth/web/start", json={"phone": PHONE})
    assert r.status_code == 429 and r.json()["detail"]["code"] == "too_many_codes"

    monkeypatch.setattr(accounts, "NEW_NUMBERS_PER_HOUR", 2)  # PHONE was the first new number this hour
    assert client.post("/auth/web/start", json={"phone": "+17345550101"}).status_code == 200
    full = client.post("/auth/web/start", json={"phone": "+17345550102"})
    assert full.status_code == 429 and full.json()["detail"]["code"] == "signups_full"
    user("+17345550103")  # already texts Hidden Rent: not a new Photon slot
    assert client.post("/auth/web/start", json={"phone": "+17345550103"}).status_code == 200

    monkeypatch.setattr(accounts, "PER_IP_10MIN", 5)  # 5 codes from this IP so far
    assert client.post("/auth/web/start", json={"phone": "+17345550103"}).json()["detail"]["code"] == "too_many_codes"
    assert client.post("/auth/web/start", json={"phone": "12"}).json()["detail"]["code"] == "bad_phone"


@pytest.fixture
def photon(monkeypatch):
    """Creds set and Photon's POST /projects/{id}/users/ faked (same user per phone, like Photon). `reply` overrides."""
    monkeypatch.setenv("PHOTON_PROJECT_ID", "proj")
    monkeypatch.setenv("PHOTON_PROJECT_SECRET", "shh")
    calls = {"made": [], "reply": None}

    def post(url, json=None, auth=None, timeout=None):
        calls["made"].append((url, json, auth))
        req = httpx.Request("POST", url)
        if calls["reply"]:
            return calls["reply"](req)
        return httpx.Response(200, request=req, json={"succeed": True, "data": {
            "id": "pu_" + json["phoneNumber"][-4:], "phoneNumber": json["phoneNumber"], "assignedPhoneNumber": "+15550001234"}})

    monkeypatch.setattr(accounts.httpx, "post", post)
    return calls


def test_web_start_allowlists_with_photon(photon):
    a = client.post("/auth/web/start", json={"phone": "734 555 0100"}).json()
    b = client.post("/auth/web/start", json={"phone": PHONE}).json()
    assert photon["made"] == [("https://spectrum.photon.codes/projects/proj/users/",
                               {"type": "shared", "phoneNumber": PHONE}, ("proj", "shh"))] * 2
    for s in (a, b):
        assert s["redirect_url"] == f"https://spectrum.photon.codes/users/pu_0100/redirect?msg=login%20{s['code']}"
        assert s["assigned_number_masked"] == "•••-•••-1234" and "shh" not in str(s)
    ok = client.post("/auth/web/confirm", json={"code": b["code"], "phone": PHONE}, headers=AGENT).json()
    assert accounts.get_user(ok["user_id"])["photon_user_id"] == "pu_0100"


@pytest.mark.parametrize("reply", [
    lambda req: httpx.Response(500, request=req, text="oops"),
    lambda req: httpx.Response(200, request=req, json={"succeed": False, "message": "limit"}),
    lambda req: (_ for _ in ()).throw(httpx.ConnectError("down", request=req)),
])
def test_photon_errors_are_503(photon, reply):
    photon["reply"] = reply
    r = client.post("/auth/web/start", json={"phone": PHONE})
    assert r.status_code == 503 and r.json()["detail"] == {
        "code": "photon_unavailable", "message": "We couldn't reach our texting service. Try again in a minute."}


def test_use_mocks_skips_photon(photon, monkeypatch):
    monkeypatch.setenv("USE_MOCKS", "1")
    s = client.post("/auth/web/start", json={"phone": PHONE}).json()
    assert s["redirect_url"].startswith("sms:&body=login%20") and photon["made"] == []


def test_moving_archives_the_old_home_and_one_active():
    uid = user()
    a = client.post("/properties", json={"user_id": uid, "address": "912 Mary St, Ann Arbor, MI"}, headers=AGENT).json()
    assert a["active"] and a["building_id"] == 4242 and a["estimate"]["grade"] == "C"
    b = client.post("/properties", json={"user_id": uid, "address": "715 Arbor St", "unit_sqft": 700}, headers=AGENT).json()
    me = client.get(f"/me/{uid}", headers=AGENT).json()
    assert me["current_property_id"] == b["property_id"]
    old = accounts.get_property(a["property_id"])
    assert not old["active"] and old["move_out_date"] and accounts.current_property(uid)["id"] == b["property_id"]
    assert me["properties"][0]["unit_sqft"] == {"value": 700, "source": "unit size sent with the address", "kind": "renter"}
    assert me["current_estimate"]["session_id"] == b["estimate"]["session_id"]
    assert not {"answers", "model_params"} & set(me["current_estimate"])

    back = client.post(f"/properties/{a['property_id']}/activate", headers=AGENT).json()
    assert back["active"] and back["move_out_date"] is None and not accounts.get_property(b["property_id"])["active"]
    with pytest.raises(sqlite3.IntegrityError), accounts._con() as con:  # I2 holds in the database itself
        con.execute("UPDATE properties SET active = 1")

    hist = client.get(f"/properties/{a['property_id']}/history", headers=AGENT).json()
    assert hist == {"property_id": a["property_id"], "snapshots": [], "bills": [], "impact": [], "commitments": []}
    stranger = {"Authorization": "Bearer nope"}
    assert client.get(f"/properties/{a['property_id']}/history", headers=stranger).status_code == 401
    assert client.post("/properties", json={"user_id": "u_missing", "address": "x"}, headers=AGENT).status_code == 404


def test_checkin_trigger_and_resolve():
    uid = user()
    none = client.post("/checkins/trigger", json={"user_id": uid}, headers=AGENT)
    assert none.status_code == 409 and none.json()["detail"]["code"] == "no_property"
    pid = client.post("/properties", json={"user_id": uid, "address": "912 Mary St"}, headers=AGENT).json()["property_id"]
    assert client.post("/checkins/trigger", json={"user_id": uid}).status_code == 401
    t = client.post("/checkins/trigger", json={"user_id": uid}, headers=AGENT).json()
    assert (t["message_hint"], t["property_id"], t["address"]) == ("still_at_address", pid, "912 MARY ST")
    assert client.get(f"/me/{uid}", headers=AGENT).json()["pending_checkin"] == t
    assert client.patch(f"/me/{uid}", json={"pending_checkin": None}, headers=AGENT).json()["pending_checkin"] is None
    client.post("/checkins/trigger", json={"user_id": uid}, headers=AGENT)
    client.post("/properties", json={"user_id": uid, "address": "715 Arbor St"}, headers=AGENT)  # "moved"
    assert client.get(f"/me/{uid}", headers=AGENT).json()["pending_checkin"] is None


def test_patch_me():
    uid = user()
    patch = lambda body: client.patch(f"/me/{uid}", json=body, headers=AGENT)
    assert patch({"leaderboard_opt_in": True}).json()["detail"]["code"] == "alias_required"
    me = patch({"alias": " Mary St Saver ", "leaderboard_opt_in": True, "timezone": "America/Chicago"}).json()
    assert (me["alias"], me["leaderboard_opt_in"], me["timezone"]) == ("Mary St Saver", True, "America/Chicago")
    assert patch({"reminder_prefs": {"hour_local": 3}}).json()["detail"]["code"] == "bad_hour"
    assert patch({"reminder_prefs": {"cadence": "hourly"}}).json()["detail"]["code"] == "bad_prefs"
    assert patch({"timezone": "Mars/Base"}).json()["detail"]["code"] == "bad_timezone"
    assert patch({"alias": "x" * 25}).json()["detail"]["code"] == "bad_alias"
    me = patch({"reminder_prefs": {"cadence": "weekly", "hour_local": 9}}).json()
    assert me["reminder_prefs"] == {"channel": "imessage", "cadence": "weekly", "hour_local": 9, "paused": False}
    assert me["alias"] == "Mary St Saver"  # untouched fields stay
