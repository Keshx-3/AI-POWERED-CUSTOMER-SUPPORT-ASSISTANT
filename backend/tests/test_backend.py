import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.tools.tool_registry import (
    hotel_tool,
    flight_tool,
    tracking_tool,
    refund_tool,
    complaint_tool,
    escalation_tool,
    execute_tool,
)
from app.services.memory_service import memory


@pytest.fixture(autouse=True)
def clear_memory():
    memory._store.clear()


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_general():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/chat", json={"message": "Hello", "conversation_id": "test-1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] in ("general", "general")
    assert "conversation_id" in data


def test_hotel_tool():
    result = hotel_tool(city="Dubai")
    assert result["city"] == "Dubai"
    assert len(result["hotels"]) == 5
    assert result["hotels"][0]["name"] == "Grand Palace Hotel"


def test_hotel_tool_filtered():
    result = hotel_tool(city="Dubai", max_price=5000)
    assert len(result["hotels"]) == 2  # Only City Inn Express & Budget Stay


def test_flight_tool():
    result = flight_tool(source="Mumbai", destination="Delhi")
    assert result["source"] == "Mumbai (BOM)"
    assert result["destination"] == "Delhi (DEL)"
    assert len(result["flights"]) == 5


def test_tracking_tool():
    result = tracking_tool(order_id="ORD-123")
    assert result["order_id"] == "ORD-123"
    assert result["status"] == "In Transit"


def test_refund_tool():
    result = refund_tool(order_id="ORD-123")
    assert result["refund_amount"] == 2499.0
    assert result["status"] == "Approved"


def test_complaint_tool():
    result = complaint_tool(category="service", description="Bad experience")
    assert result["status"] == "Filed"
    assert "TKT-" in result["ticket_id"]


def test_escalation_tool():
    result = escalation_tool(reason="Not satisfied")
    assert result["priority"] == "High"
    assert "ESC-" in result["ticket_id"]


def test_execute_hotel_tool():
    result = execute_tool("hotel_search", {"city": "Dubai"})
    assert result["intent"] == "hotel_search"
    assert "hotels" in result["result"]


def test_execute_unknown_tool():
    result = execute_tool("unknown_intent")
    assert "error" in result["result"]


def test_memory():
    from app.schemas.models import Message
    memory.add_message("conv-1", Message(role="user", content="Hello"))
    memory.add_message("conv-1", Message(role="assistant", content="Hi there"))
    hist = memory.get_history("conv-1")
    assert len(hist) == 2
    assert hist[0].content == "Hello"


@pytest.mark.asyncio
async def test_chat_follow_up():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.post("/api/v1/chat", json={"message": "Show hotels in Dubai", "conversation_id": "followup-test"})
        assert resp1.status_code == 200
        resp2 = await client.post("/api/v1/chat", json={"message": "Show cheaper ones", "conversation_id": "followup-test"})
        assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_invalid_empty_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/chat", json={"message": "", "conversation_id": "test"})
    assert resp.status_code == 422
