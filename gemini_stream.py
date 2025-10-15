# pip install google-genai pydantic ijson
"""
Gemini streaming structured output API that mimics OpenAI's interface
"""
import os
from typing import List, Optional, Type, Iterator, Any
from dataclasses import dataclass
from enum import Enum
from io import BytesIO

import ijson
from google import genai
from google.genai import types
from pydantic import BaseModel


class EventType(str, Enum):
    """Event types emitted during streaming"""
    OUTPUT_DELTA = "response.output_text.delta"
    ITEM_PARSED = "response.item.parsed"
    COMPLETED = "response.completed"
    ERROR = "response.error"


@dataclass
class StreamEvent:
    """Base class for stream events"""
    type: EventType
    delta: Optional[str] = None
    item: Optional[dict] = None
    error: Optional[str] = None


class IncrementalItemParser:
    """Parses JSON items incrementally as they arrive"""
    def __init__(self, array_path: str = 'items.item'):
        self.array_path = array_path
        self.array_prefix = '.'.join(array_path.split('.')[:-1])
        self.current_item = None
        self.seen_count = 0

    def process_events(self, events):
        """Process ijson events and yield complete items"""
        item_count = 0
        for prefix, event, value in events:
            # Start of an item object
            if prefix == self.array_path and event == 'start_map':
                self.current_item = {}

            # Key-value pair within an item
            elif prefix.startswith(f'{self.array_path}.'):
                key = prefix.replace(f'{self.array_path}.', '')
                if event in ('string', 'number', 'boolean', 'null'):
                    self.current_item[key] = value

            # End of an item object
            elif prefix == self.array_path and event == 'end_map':
                item_count += 1
                # Only yield if this is a new item we haven't seen before
                if item_count > self.seen_count:
                    self.seen_count += 1
                    yield self.current_item
                self.current_item = None


class StreamResponse:
    """Manages streaming response similar to OpenAI's interface"""

    def __init__(
        self,
        client: genai.Client,
        model: str,
        input: List[dict],
        text_format: Type[BaseModel],
        array_path: Optional[str] = 'items.item'
    ):
        self.client = client
        self.model = model
        self.input = input
        self.text_format = text_format
        self.array_path = array_path
        self.buffer = b""
        self.parser = IncrementalItemParser(array_path) if array_path else None
        self.final_response = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self) -> Iterator[StreamEvent]:
        """Iterate over stream events"""
        # Convert OpenAI-style messages to Gemini format
        contents = self._convert_messages(self.input)

        # Configure Gemini for structured output
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.text_format,
        )

        # Stream from Gemini
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                # Emit text delta event
                yield StreamEvent(
                    type=EventType.OUTPUT_DELTA,
                    delta=chunk.text
                )

                # Accumulate buffer and try to parse items if parser is configured
                self.buffer += chunk.text.encode('utf-8')

                if self.parser:
                    try:
                        events = ijson.parse(BytesIO(self.buffer))
                        for item in self.parser.process_events(events):
                            # Emit item parsed event
                            yield StreamEvent(
                                type=EventType.ITEM_PARSED,
                                item=item
                            )
                    except ijson.IncompleteJSONError:
                        # Not enough data yet, continue
                        pass
                    except Exception as e:
                        # Other parsing errors
                        yield StreamEvent(
                            type=EventType.ERROR,
                            error=str(e)
                        )

        # Parse final complete response
        try:
            self.final_response = self.text_format.model_validate_json(self.buffer)
            yield StreamEvent(type=EventType.COMPLETED)
        except Exception as e:
            yield StreamEvent(
                type=EventType.ERROR,
                error=f"Failed to parse final response: {e}"
            )

    def _convert_messages(self, messages: List[dict]) -> str:
        """Convert OpenAI-style messages to Gemini prompt"""
        # Simple conversion - combine messages
        parts = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'system':
                parts.append(f"System: {content}")
            elif role == 'user':
                parts.append(f"User: {content}")
        return "\n\n".join(parts)

    def get_final_response(self) -> Optional[BaseModel]:
        """Get the final parsed response"""
        return self.final_response


class GeminiClient:
    """Client for Gemini API with OpenAI-style streaming interface"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.responses = self

    def stream(
        self,
        model: str,
        input: List[dict],
        text_format: Type[BaseModel],
        array_path: Optional[str] = 'items.item'
    ) -> StreamResponse:
        """
        Stream structured output from Gemini

        Args:
            model: Model name (e.g., "gemini-2.5-flash")
            input: List of message dicts with 'role' and 'content'
            text_format: Pydantic model defining the output structure
            array_path: JSON path to array items (default: 'items.item', None for non-array)

        Returns:
            StreamResponse object that yields events
        """
        return StreamResponse(
            client=self.client,
            model=model,
            input=input,
            text_format=text_format,
            array_path=array_path
        )
