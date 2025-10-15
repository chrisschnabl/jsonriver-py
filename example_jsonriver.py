#!/usr/bin/env python
"""
Example usage of the jsonriver library

This demonstrates how to use jsonriver to parse JSON incrementally
as it streams in.
"""

import asyncio
import json
from jsonriver import parse


async def make_stream_of_chunks(text: str, chunk_size: int):
    """Simulate a streaming JSON source"""
    for i in range(0, len(text), chunk_size):
        await asyncio.sleep(0.01)  # Simulate network delay
        yield text[i:i + chunk_size]


async def example_basic():
    """Basic example of parsing streaming JSON"""
    print("=== Basic Example ===")

    json_data = {"name": "Alice", "age": 30, "city": "New York"}
    json_str = json.dumps(json_data)

    print(f"Original JSON: {json_str}")
    print("\nIncremental parsing results:")

    stream = make_stream_of_chunks(json_str, chunk_size=3)
    async for value in parse(stream):
        print(f"  {json.dumps(value)}")

    print()


async def example_array():
    """Example with an array"""
    print("=== Array Example ===")

    json_data = ["apple", "banana", "cherry"]
    json_str = json.dumps(json_data)

    print(f"Original JSON: {json_str}")
    print("\nIncremental parsing results:")

    stream = make_stream_of_chunks(json_str, chunk_size=2)
    async for value in parse(stream):
        print(f"  {json.dumps(value)}")

    print()


async def example_nested():
    """Example with nested structure"""
    print("=== Nested Structure Example ===")

    json_data = {
        "user": {
            "name": "Bob",
            "hobbies": ["reading", "coding", "hiking"]
        },
        "active": True
    }
    json_str = json.dumps(json_data)

    print(f"Original JSON: {json_str}")
    print("\nIncremental parsing results:")

    stream = make_stream_of_chunks(json_str, chunk_size=5)
    async for value in parse(stream):
        print(f"  {json.dumps(value)}")

    print()


async def main():
    """Run all examples"""
    await example_basic()
    await example_array()
    await example_nested()

    print("All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
