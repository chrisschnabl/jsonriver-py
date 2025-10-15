#!/usr/bin/env python3
"""
Example matching the OpenAI API example with entity extraction
"""
from typing import List
from pydantic import BaseModel
from gemini_stream import GeminiClient, EventType


class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]


# Create client
client = GeminiClient()

print("Extracting entities from text...\n")
print("=" * 60)

with client.responses.stream(
    model="gemini-2.5-flash",
    input=[
        {"role": "system", "content": "Extract entities from the input text"},
        {
            "role": "user",
            "content": "The quick brown fox jumps over the lazy dog with piercing blue eyes",
        },
    ],
    text_format=EntitiesModel,
    array_path=None  # Not parsing array items, parsing the whole object
) as stream:
    for event in stream:
        if event.type == EventType.OUTPUT_DELTA:
            print(event.delta, end="", flush=True)

        elif event.type == EventType.ITEM_PARSED:
            print(f"\n\n✓ Entity parsed: {event.item}")

        elif event.type == EventType.ERROR:
            # Errors are expected if not parsing arrays
            pass

        elif event.type == EventType.COMPLETED:
            print("\n\n" + "=" * 60)
            print("Completed")

    final_response = stream.get_final_response()
    print(f"\nFinal response:\n{final_response}")
    print(f"\nAttributes: {final_response.attributes}")
    print(f"Colors: {final_response.colors}")
    print(f"Animals: {final_response.animals}")
