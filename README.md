# AI-Powered Customer Support Assistant

A fully offline, local AI-powered customer support assistant built with **Python (FastAPI)**, **Ollama (local LLM)**, and **Flutter**.

## Architecture

```
User → Flutter App → POST /api/v1/chat → FastAPI → Ollama (intent classification)
                                                   → Tool Registry (mock execution)
                                                   → Memory Service (context)
                   ← JSON response (reply + ui_type + data)
                   → Dynamic UI rendering (HotelWidget, FlightWidget, InfoCard)
```

### Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point, CORS, routes
│   ├── routes/chat.py       # POST /api/v1/chat endpoint
│   ├── schemas/models.py    # Pydantic request/response models
│   ├── services/
│   │   ├── llm_service.py   # Ollama integration + prompt engineering
│   │   └── memory_service.py # In-memory conversation context (last 5 turns)
│   └── tools/
│       └── tool_registry.py  # 6 mock tools + execution engine
├── tests/test_backend.py    # 14 passing tests
├── requirements.txt
└── pyproject.toml
```

### Frontend Structure

```
frontend/
├── lib/
│   ├── main.dart                     # App entry point
│   ├── models/
│   │   ├── chat_message.dart         # Message data model
│   │   └── chat_response.dart        # API response model
│   ├── services/
│   │   └── api_service.dart          # HTTP client for backend
│   └── widgets/
│       ├── chat_screen.dart          # Main chat UI + dynamic rendering
│       ├── hotel_widget.dart         # Hotel cards with name/price/rating
│       ├── flight_widget.dart        # Flight cards with details
│       └── info_card.dart            # Generic info (tracking/refund/etc.)
└── test/widget_test.dart
```

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Ollama | Latest | Local LLM |
| Flutter | 3.x | Frontend framework |
| Dart | 3.x | Frontend language |

## Setup Instructions

### 1. Ollama (Local LLM)

```bash
# Install from https://ollama.com/download
# Then pull a small model:
ollama pull llama3.2:1b

# Verify:
ollama list
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt

# Start the server:
$env:PYTHONPATH = "$pwd"
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
flutter pub get
flutter run
```

> **Note for Android emulator**: The API URL defaults to `10.0.2.2:8000`. For Windows desktop, change `ApiService._baseUrl` to `http://localhost:8000/api/v1`.

## API Usage

### POST /api/v1/chat

**Request:**
```json
{
  "message": "Show hotels in Dubai",
  "conversation_id": "user-123",
  "history": []
}
```

**Response:**
```json
{
  "reply": "Found 5 hotel(s) in Dubai.",
  "ui_type": "hotel_list",
  "data": {
    "city": "Dubai",
    "hotels": [
      {
        "name": "Grand Palace Hotel",
        "price_per_night": 15000,
        "rating": 4.8,
        "location": "Dubai Marina",
        "image_url": ""
      }
    ],
    "total": 5
  },
  "intent": "hotel_search",
  "conversation_id": "user-123"
}
```

### curl Example

```bash
curl -Method POST -ContentType "application/json" -Body '{"message": "Show hotels in Dubai", "conversation_id": "test"}' http://localhost:8000/api/v1/chat
```

## Supported Intents

| Intent | Tool | ui_type | Description |
|--------|------|---------|-------------|
| `hotel_search` | `hotel_tool()` | `hotel_list` | Search hotels by city & price |
| `flight_search` | `flight_tool()` | `flight_list` | Search flights by route |
| `order_tracking` | `tracking_tool()` | `tracking_info` | Track order status |
| `refund_request` | `refund_tool()` | `refund_info` | Process refund requests |
| `complaint` | `complaint_tool()` | `complaint_status` | File complaints |
| `escalation` | `escalation_tool()` | `escalation_status` | Escalate to manager |
| `general` | — | `null` | Greetings/chitchat |

## Conversation Memory

The system maintains the last 3-5 conversation turns per `conversation_id`. Follow-up questions like "Show cheaper ones" after a hotel search will correctly reference the previous context.

## Testing

```bash
cd backend
$env:PYTHONPATH = "$pwd"
pytest -v
```

## Design Decisions

- **Prompt engineering** over fine-tuning: A detailed system prompt with examples ensures reliable JSON output from the LLM
- **Fallback classifier**: Rule-based keyword matching kicks in if Ollama is unavailable
- **Temperature 0.1**: Keeps LLM responses deterministic
- **Short memory (5 turns)**: Balances context awareness with token budget
- **Schema validation**: Pydantic models enforce strict JSON structure on all API responses
