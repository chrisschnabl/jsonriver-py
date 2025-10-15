#!/usr/bin/env python3
"""
Example usage of Gemini streaming API with OpenAI-style interface
"""
from typing import List
from pydantic import BaseModel
from gemini_stream import GeminiClient, EventType


# Define your output schema
class Item(BaseModel):
    id: str
    score: float


class ItemList(BaseModel):
    items: List[Item]


# Create client
client = GeminiClient()

# Stream structured output
print("Streaming structured output from Gemini...\n")
print("=" * 60)

with client.responses.stream(
    model="gemini-2.5-flash",
    input=[
        {"role": "system", "content": "You are a helpful assistant that generates test data"},
        {
            "role": "user",
            "content": "Generate 5 items with 'id' and 'score' fields. Scores should be between 0 and 1.",
        },
    ],
    text_format=ItemList,
    array_path='items.item'  # Path to items in the JSON
) as stream:
    for event in stream:
        if event.type == EventType.OUTPUT_DELTA:
            # Raw JSON chunk
            print(event.delta, end="", flush=True)

        elif event.type == EventType.ITEM_PARSED:
            # Item was fully parsed
            print(f"\n\n✓ Item parsed: {event.item}")

        elif event.type == EventType.ERROR:
            print(f"\n\nError: {event.error}")

        elif event.type == EventType.COMPLETED:
            print("\n\n" + "=" * 60)
            print("Stream completed!")

    # Get final parsed response
    final_response = stream.get_final_response()
    print(f"\nFinal response type: {type(final_response)}")
    print(f"Total items: {len(final_response.items)}")
    print("\nAll items:")
    for item in final_response.items:
        print(f"  - {item.id}: {item.score}")
