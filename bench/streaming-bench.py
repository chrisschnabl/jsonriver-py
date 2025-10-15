#!/usr/bin/env python
"""
Streaming benchmark for jsonriver Python implementation

Demonstrates the value proposition: time-to-first-value and incremental updates.

Copyright (c) 2024 jsonriver-python contributors
SPDX-License-Identifier: BSD-3-Clause
"""

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

# Add parent directory to path to import jsonriver
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jsonriver import parse


def load_test_data():
    """Load the test JSON files"""
    base_path = Path(__file__).parent.parent / "vendor" / "testdata"

    with open(base_path / "medium-file.json", "r", encoding="utf-8") as f:
        medium_json = f.read()

    return medium_json


async def chunked_stream(text: str, chunk_size: int, delay_ms: float = 0):
    """Convert string to chunked async stream with optional delay"""
    for i in range(0, len(text), chunk_size):
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)
        yield text[i : i + chunk_size]


async def jsonriver_streaming(json_string: str, chunk_size: int):
    """Parse JSON using jsonriver with chunked input"""
    first_value_time = None
    start = time.perf_counter()

    final_value = None
    async for val in parse(chunked_stream(json_string, chunk_size)):
        if first_value_time is None:
            first_value_time = time.perf_counter() - start
        final_value = val

    total_time = time.perf_counter() - start
    return total_time, first_value_time, final_value


async def json_loads_streaming(json_string: str, chunk_size: int):
    """Simulate json.loads with chunked input (must wait for all)"""
    start = time.perf_counter()

    # Collect all chunks first (simulating waiting for complete data)
    chunks = []
    async for chunk in chunked_stream(json_string, chunk_size):
        chunks.append(chunk)

    # Now parse
    complete_string = "".join(chunks)
    result = json.loads(complete_string)

    total_time = time.perf_counter() - start
    first_value_time = total_time  # Can only get value after everything arrives

    return total_time, first_value_time, result


async def benchmark_streaming(json_str: str, chunk_size: int, num_times: int):
    """Benchmark streaming scenarios"""
    jsonriver_total_times = []
    jsonriver_first_times = []
    jsonloads_total_times = []
    jsonloads_first_times = []

    print(f"Running streaming benchmark with {chunk_size} byte chunks...", end="", flush=True)

    for i in range(num_times):
        if i % max(1, num_times // 10) == 0:
            print(".", end="", flush=True)

        # Benchmark jsonriver
        total, first, _ = await jsonriver_streaming(json_str, chunk_size)
        jsonriver_total_times.append(total * 1000)  # to ms
        jsonriver_first_times.append(first * 1000)

        # Benchmark json.loads
        total, first, _ = await json_loads_streaming(json_str, chunk_size)
        jsonloads_total_times.append(total * 1000)
        jsonloads_first_times.append(first * 1000)

    print(" done!\n")

    # Report results
    file_size_kb = len(json_str) / 1024
    num_chunks = (len(json_str) + chunk_size - 1) // chunk_size

    print(f"File size: {file_size_kb:.1f} KB, Chunk size: {chunk_size} bytes, Chunks: {num_chunks}")
    print(f"Averaged over {num_times} runs\n")

    print("Total parsing time:")
    print(
        f"  jsonriver (streaming)  {statistics.mean(jsonriver_total_times):>10.3f}ms "
        f"±{statistics.stdev(jsonriver_total_times):.2f}ms"
    )
    print(
        f"  json.loads (buffered)  {statistics.mean(jsonloads_total_times):>10.3f}ms "
        f"±{statistics.stdev(jsonloads_total_times):.2f}ms"
    )

    print("\nTime to first value:")
    print(
        f"  jsonriver              {statistics.mean(jsonriver_first_times):>10.3f}ms "
        f"±{statistics.stdev(jsonriver_first_times):.2f}ms"
    )
    print(
        f"  json.loads             {statistics.mean(jsonloads_first_times):>10.3f}ms "
        f"±{statistics.stdev(jsonloads_first_times):.2f}ms (must wait for all data)"
    )

    # Calculate the speedup for time-to-first-value
    speedup = statistics.mean(jsonloads_first_times) / statistics.mean(jsonriver_first_times)
    print(f"\n  → jsonriver is {speedup:.1f}x faster to first value!\n")


async def benchmark_progressive_updates(json_str: str, chunk_size: int):
    """Demonstrate progressive updates - a key benefit of jsonriver"""
    print("Progressive updates demonstration:")
    print(f"Parsing {len(json_str)/1024:.1f} KB in {chunk_size} byte chunks\n")

    start = time.perf_counter()
    update_count = 0

    async for val in parse(chunked_stream(json_str, chunk_size)):
        update_count += 1

    total_time = (time.perf_counter() - start) * 1000

    print(f"  Updates received: {update_count}")
    print(f"  Total time: {total_time:.3f}ms")
    print(f"  Average time between updates: {total_time/update_count:.3f}ms")
    print(
        f"\n  → User sees {update_count} progressive updates instead of waiting {total_time:.1f}ms\n"
    )


async def main():
    """Run streaming benchmarks"""
    print("\n" + "=" * 70)
    print("jsonriver Python Streaming Benchmark")
    print("=" * 70 + "\n")

    print("Loading test data...")
    json_str = load_test_data()
    print(f"Loaded {len(json_str)/1024:.1f} KB of JSON data\n")

    # Benchmark with different chunk sizes
    print("="*70)
    await benchmark_streaming(json_str, chunk_size=1024, num_times=100)

    print("="*70)
    await benchmark_streaming(json_str, chunk_size=8192, num_times=100)

    print("="*70)
    await benchmark_progressive_updates(json_str, chunk_size=4096)

    print("="*70)
    print("Benchmark complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
