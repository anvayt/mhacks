"""Optional model discovery is safe against old servers and transient failures."""
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore

import httpx
import pytest

from app import estimate, model_capabilities


@pytest.fixture(autouse=True)
def clear(monkeypatch):
    monkeypatch.setattr(estimate, "MODEL_BASE_URL", "http://model.test")
    model_capabilities.reset_cache()
    yield
    model_capabilities.reset_cache()


def test_supported_response_is_cached_and_not_mutable(monkeypatch):
    calls = []
    def get(url, timeout):
        calls.append(url)
        return httpx.Response(200, json={"estimate_params": ["air_sealing"], "endpoints": ["lookalikes"],
                                        "bill_noise_bases": ["within_building"], "details": {}})
    monkeypatch.setattr(model_capabilities.httpx, "get", get)
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda _: model_capabilities.capabilities(), range(4)))
    results[0]["estimate_params"].append("invented")
    assert model_capabilities.capabilities()["estimate_params"] == ["air_sealing"]
    assert calls == ["http://model.test/hc/capabilities"]


@pytest.mark.parametrize("status,body", [(404, {}), (503, {}), (200, []), (200, {"estimate_params": "air_sealing"}),
                                         (200, {"endpoints": [42]}), (200, {"details": None}),
                                         (200, {"unrelated": True})])
def test_old_or_malformed_endpoint_advertises_nothing(monkeypatch, status, body):
    monkeypatch.setattr(model_capabilities.httpx, "get", lambda *a, **k: httpx.Response(status, json=body))
    assert model_capabilities.capabilities() == {}


@pytest.mark.parametrize("error", [httpx.ConnectError("offline"), httpx.ReadTimeout("timeout"), ValueError("bad JSON")])
def test_fetch_failure_is_safe_and_cached(monkeypatch, error):
    calls = []
    def get(*a, **k):
        calls.append(1)
        raise error
    monkeypatch.setattr(model_capabilities.httpx, "get", get)
    assert model_capabilities.capabilities() == model_capabilities.capabilities() == {}
    assert len(calls) == 1


def test_ttl_reset_and_model_url_refresh(monkeypatch):
    now, calls = [0.0], []
    monkeypatch.setattr(model_capabilities, "monotonic", lambda: now[0])
    def get(url, **k):
        calls.append(url)
        return httpx.Response(200, json={"endpoints": [str(len(calls))]})
    monkeypatch.setattr(model_capabilities.httpx, "get", get)
    assert model_capabilities.capabilities()["endpoints"] == ["1"]
    now[0] = model_capabilities.TTL_SECONDS
    assert model_capabilities.capabilities()["endpoints"] == ["2"]
    monkeypatch.setattr(estimate, "MODEL_BASE_URL", "http://other.test/")
    assert model_capabilities.capabilities()["endpoints"] == ["3"]
    assert calls[-1] == "http://other.test/hc/capabilities"
    model_capabilities.reset_cache()
    assert model_capabilities.capabilities()["endpoints"] == ["4"]


def test_probe_shares_the_model_concurrency_limit(monkeypatch):
    slots = BoundedSemaphore(1)
    monkeypatch.setattr(estimate, "MODEL_SLOTS", slots)
    def get(*a, **k):
        assert not slots.acquire(blocking=False)
        return httpx.Response(200, json={"endpoints": []})
    monkeypatch.setattr(model_capabilities.httpx, "get", get)
    assert model_capabilities.capabilities() == {"endpoints": []}
    assert slots.acquire(blocking=False)
    slots.release()
