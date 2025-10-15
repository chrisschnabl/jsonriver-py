#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "langchain-openai>=0.2.0",
#   "pydantic>=2.0.0",
#   "ijson>=3.3.0",
# ]
# ///

from typing import List
from io import BytesIO
from pydantic import BaseModel
import ijson
from langchain_openai import ChatOpenAI

class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]

class IncrementalParser:
    """Parse JSON incrementally and emit complete fields/array items"""
    def __init__(self):
        self.buffer = b""
        self.completed_fields = set()

    def add_chunk(self, chunk: str):
        """Add a chunk of JSON text and try to parse what we can"""
        self.buffer += chunk.encode('utf-8')

        try:
            # Try to parse what we have so far
            events = list(ijson.parse(BytesIO(self.buffer)))

            # Track which arrays/fields are complete
            for prefix, event_type, value in events:
                # Check for completed arrays
                if event_type == 'end_array':
                    field_name = prefix.split('.')[0] if '.' in prefix else prefix
                    if field_name and field_name not in self.completed_fields:
                        # Extract the completed array
                        array_values = self._extract_array(events, field_name)
                        if array_values is not None:
                            self.completed_fields.add(field_name)
                            yield {
                                'type': 'field_completed',
                                'field': field_name,
                                'value': array_values
                            }

        except ijson.IncompleteJSONError:
            # Not enough data yet
            pass
        except Exception as e:
            yield {
                'type': 'error',
                'error': str(e)
            }

    def _extract_array(self, events, field_name: str):
        """Extract array values from parsed events"""
        values = []
        in_target_array = False

        for prefix, event_type, value in events:
            if prefix == field_name and event_type == 'start_array':
                in_target_array = True
            elif prefix == f"{field_name}.item" and event_type == 'string':
                if in_target_array:
                    values.append(value)
            elif prefix == field_name and event_type == 'end_array':
                in_target_array = False
                return values

        return None if not values else values

    def get_final_model(self, model_class: type[BaseModel]):
        """Parse the complete buffer into the final model"""
        try:
            return model_class.model_validate_json(self.buffer)
        except Exception as e:
            return None

# Create LangChain client with JSON mode
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}}
)

print("Starting LangChain streaming test with incremental parsing...\n")
print("=" * 60)

# Create prompt for JSON extraction
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content=f"Extract entities from the input text and return them in this JSON format: {EntitiesModel.model_json_schema()}"),
    HumanMessage(content="The quick brown fox jumps over the lazy dog with piercing blue eyes")
]

try:
    parser = IncrementalParser()
    accumulated_text = ""

    # Stream the response
    for chunk in llm.stream(messages):
        # Get the content delta
        if chunk.content:
            text_delta = chunk.content
            accumulated_text += text_delta
            print(f"{text_delta}", end="", flush=True)

            # Try to parse incrementally
            for event in parser.add_chunk(text_delta):
                if event['type'] == 'field_completed':
                    print(f"\n\n✓ Field '{event['field']}' completed: {event['value']}")
                elif event['type'] == 'error':
                    print(f"\n⚠ Parse error: {event['error']}")

    print("\n" + "=" * 60)
    print("Completed")

    # Try to get final model from incremental parser
    final_model = parser.get_final_model(EntitiesModel)
    if final_model:
        print(f"\nParsed from stream buffer:")
        print(f"  Attributes: {final_model.attributes}")
        print(f"  Colors: {final_model.colors}")
        print(f"  Animals: {final_model.animals}")

except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
