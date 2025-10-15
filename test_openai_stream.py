#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.58.1",
#   "pydantic>=2.0.0",
# ]
# ///

from typing import List
from openai import OpenAI
from pydantic import BaseModel

class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]

client = OpenAI()

print("Starting OpenAI streaming test with structured outputs...\n")

try:
    with client.responses.stream(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": "Extract entities from the input text"},
            {
                "role": "user",
                "content": "The quick brown fox jumps over the lazy dog with piercing blue eyes",
            },
        ],
        text_format=EntitiesModel,
    ) as stream:
        for event in stream:
            print(f"Event type: {event.type}")

            if event.type == "response.refusal.delta":
                print(f"  Refusal delta: {event.delta}")
            elif event.type == "response.output_text.delta":
                print(f"  Output text delta: {event.delta}", end="", flush=True)
            elif event.type == "response.error":
                print(f"  Error: {event.error}")
            elif event.type == "response.completed":
                print("\n✓ Response completed")

        final_response = stream.get_final_response()
        print(f"\nFinal response:\n{final_response}")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
