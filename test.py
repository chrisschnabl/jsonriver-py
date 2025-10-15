# pip install google-genai pydantic ijson
import json
import os
import sys
from typing import List
import ijson
from io import BytesIO

from google import genai
from google.genai import types
from pydantic import BaseModel


# 1) Define the JSON shape you want back
class Item(BaseModel):
    id: str
    score: float


class ItemList(BaseModel):
    items: List[Item]


# 2) Create the client (uses GOOGLE_API_KEY env var if not passed explicitly)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 3) Ask Gemini to stream JSON matching your schema
prompt = "Produce 5 items with 'id' and 'score' in [0,1]. Keep it concise."
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=ItemList,  # Pydantic -> JSON Schema is auto-generated
)

print("--- Streaming and parsing incrementally ---\n")

# Event-based incremental parser
class IncrementalItemParser:
    def __init__(self):
        self.current_item = None
        self.seen_count = 0  # Track how many items we've already yielded

    def process_events(self, events):
        """Process ijson events and yield only new complete items"""
        item_count = 0
        for prefix, event, value in events:
            # Debug: print all events
            #print(f"\n[Event: {prefix}, {event}, {value}]")

            # Start of an item object
            if prefix == 'items.item' and event == 'start_map':
                self.current_item = {}

            # Key-value pair within an item
            elif prefix.startswith('items.item.'):
                key = prefix.replace('items.item.', '')
                if event in ('string', 'number', 'boolean'):
                    self.current_item[key] = value

            # End of an item object
            elif prefix == 'items.item' and event == 'end_map':
                item_count += 1
                print(f"\n[Parser: item {item_count}, seen {self.seen_count}]", end="")
                # Only yield if this is a new item we haven't seen before
                if item_count > self.seen_count:
                    self.seen_count += 1
                    yield self.current_item
                self.current_item = None

# Use ijson's low-level parse function with incremental feeding
parser = IncrementalItemParser()
buffer = b""

print("Raw JSON stream:")
chunk_num = 0
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config,
):
    if chunk.text:
        chunk_num += 1
        print(f"\n[Chunk {chunk_num}: {len(chunk.text)} chars]", end=" ")
        sys.stdout.write(chunk.text)
        sys.stdout.flush()
        buffer += chunk.text.encode('utf-8')

        # Try parsing the accumulated buffer
        try:
            events = ijson.parse(BytesIO(buffer))
            for item in parser.process_events(events):
                print(f"\n  ✓ Parsed item: {item}")
        except ijson.IncompleteJSONError as e:
            # Not enough data yet, continue
            print(f"\n[Incomplete JSON: {e}]", end="")
        except Exception as e:
            # Other errors, likely incomplete JSON
            print(f"\n[Parse error: {type(e).__name__}: {e}]", end="")

print("\n\nDone!")
