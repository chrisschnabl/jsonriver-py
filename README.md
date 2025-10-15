# Gemini Streaming Structured Output API

An OpenAI-compatible streaming API for Google's Gemini that provides **incremental JSON parsing** - see items/objects as soon as they're complete, not just when the entire response finishes.

## Features

- **Incremental parsing**: Get notified as soon as each item in an array is complete
- **OpenAI-style interface**: Familiar event-based streaming API
- **Pydantic schemas**: Define output structure with type safety
- **Flexible**: Works with both array and non-array responses

## Installation

```bash
pip install google-genai pydantic ijson
```

## Quick Start

### Example 1: Streaming Array Items

Parse items from an array incrementally as they arrive:

```python
from typing import List
from pydantic import BaseModel
from gemini_stream import GeminiClient, EventType


class Item(BaseModel):
    id: str
    score: float


class ItemList(BaseModel):
    items: List[Item]


client = GeminiClient()

with client.responses.stream(
    model="gemini-2.5-flash",
    input=[
        {"role": "system", "content": "Generate test data"},
        {"role": "user", "content": "Generate 5 items with id and score"},
    ],
    text_format=ItemList,
    array_path='items.item'  # Parse items from the 'items' array
) as stream:
    for event in stream:
        if event.type == EventType.OUTPUT_DELTA:
            # Raw JSON chunk
            print(event.delta, end="", flush=True)

        elif event.type == EventType.ITEM_PARSED:
            # Item was fully parsed!
            print(f"\n✓ Got item: {event.item}")

        elif event.type == EventType.COMPLETED:
            print("\nStream completed!")

    # Get final typed response
    final = stream.get_final_response()
    print(f"Total items: {len(final.items)}")
```

### Example 2: Entity Extraction (Non-Array)

For responses that aren't arrays, set `array_path=None`:

```python
from typing import List
from pydantic import BaseModel
from gemini_stream import GeminiClient, EventType


class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]


client = GeminiClient()

with client.responses.stream(
    model="gemini-2.5-flash",
    input=[
        {"role": "system", "content": "Extract entities from text"},
        {"role": "user", "content": "The quick brown fox jumps over the lazy dog"},
    ],
    text_format=EntitiesModel,
    array_path=None  # Not parsing array items
) as stream:
    for event in stream:
        if event.type == EventType.OUTPUT_DELTA:
            print(event.delta, end="", flush=True)
        elif event.type == EventType.COMPLETED:
            print("\nCompleted!")

    final = stream.get_final_response()
    print(f"Colors: {final.colors}")
    print(f"Animals: {final.animals}")
```

## Event Types

The API emits the following event types:

- `EventType.OUTPUT_DELTA`: Raw JSON text chunk received
- `EventType.ITEM_PARSED`: Complete item from array was parsed (only when using `array_path`)
- `EventType.COMPLETED`: Stream finished successfully
- `EventType.ERROR`: Parsing or streaming error occurred

## API Reference

### `GeminiClient`

```python
client = GeminiClient(api_key: Optional[str] = None)
```

Creates a Gemini client. If `api_key` is not provided, uses `GOOGLE_API_KEY` environment variable.

### `client.responses.stream()`

```python
stream(
    model: str,
    input: List[dict],
    text_format: Type[BaseModel],
    array_path: Optional[str] = 'items.item'
) -> StreamResponse
```

**Parameters:**
- `model`: Model name (e.g., `"gemini-2.5-flash"`)
- `input`: List of message dicts with `'role'` and `'content'`
- `text_format`: Pydantic model defining the output structure
- `array_path`: JSON path to array items (default: `'items.item'`, use `None` for non-array responses)

**Returns:** `StreamResponse` object that yields events

### `StreamEvent`

Each event has:
- `type`: One of the `EventType` enum values
- `delta`: Text chunk (when `type == OUTPUT_DELTA`)
- `item`: Parsed item dict (when `type == ITEM_PARSED`)
- `error`: Error message (when `type == ERROR`)

## How It Works

The library uses `ijson` for true incremental JSON parsing:

1. **Streaming**: Gemini streams JSON text in chunks
2. **Incremental parsing**: As each chunk arrives, `ijson` parses it without waiting for the complete response
3. **Item detection**: When a complete item in the array is parsed, an `ITEM_PARSED` event is emitted
4. **Deduplication**: Already-seen items are tracked so they're only emitted once

This means you can start processing items **before the entire response arrives**, making it perfect for:
- Real-time UIs
- Large array responses
- Streaming data pipelines
- Server-sent events (SSE)

## Comparison to OpenAI

This API closely mirrors OpenAI's structured output streaming, but with Gemini:

```python
# OpenAI
with openai_client.responses.stream(...) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            ...

# Gemini (this library)
with gemini_client.responses.stream(...) as stream:
    for event in stream:
        if event.type == EventType.OUTPUT_DELTA:
            ...
```

## Examples

Run the included examples:

```bash
python example.py              # Array items
python example_entities.py     # Entity extraction
```

## Requirements

- Python 3.8+
- `google-genai`
- `pydantic`
- `ijson`
