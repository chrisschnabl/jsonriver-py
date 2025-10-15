#!/usr/bin/env python
"""
Benchmark script for jsonriver Python implementation

Compares performance of jsonriver vs json.loads on different file sizes.

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

    with open(base_path / "small-file.json", "r", encoding="utf-8") as f:
        small_json = f.read()

    with open(base_path / "medium-file.json", "r", encoding="utf-8") as f:
        medium_json = f.read()

    with open(base_path / "large-file.json", "r", encoding="utf-8") as f:
        large_json = f.read()

    return small_json, medium_json, large_json


async def to_stream(text: str):
    """Convert string to async stream"""
    yield text


async def jsonriver_parse(json_string: str):
    """Parse JSON using jsonriver"""
    final_value = None
    async for val in parse(to_stream(json_string)):
        final_value = val
    return final_value


def json_loads_parse(json_string: str):
    """Parse JSON using json.loads"""
    return json.loads(json_string)


async def benchmark_file(comparisons, json_str: str, name: str, num_times: int):
    """Benchmark parsing of a file"""
    times = {comp["name"]: [] for comp in comparisons}

    print(f"Running {name}...", end="", flush=True)
    for i in range(num_times):
        if i % max(1, num_times // 10) == 0:  # Show progress every 10%
            print(".", end="", flush=True)
        for comparison in comparisons:
            start = time.perf_counter()
            if comparison["async"]:
                await comparison["parse"](json_str)
            else:
                comparison["parse"](json_str)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times[comparison["name"]].append(elapsed)
    print(" done!")

    # Report mean and standard deviation
    print(f"Parsing {name} averaged over {num_times} runs")
    for comparison in comparisons:
        name_str = comparison["name"]
        time_list = times[name_str]
        mean_time = statistics.mean(time_list)
        std_dev = statistics.stdev(time_list) if len(time_list) > 1 else 0.0

        print(f"  {name_str.ljust(25)} {mean_time:>10.3f}ms ±{std_dev:.2f}ms")
    print("\n")


async def main():
    """Run all benchmarks"""
    print("Loading test data...")
    small_json, medium_json, large_json = load_test_data()

    comparisons = [
        {
            "name": "jsonriver (Python)",
            "parse": jsonriver_parse,
            "async": True,
        },
        {
            "name": "json.loads",
            "parse": json_loads_parse,
            "async": False,
        },
    ]

    print("\n" + "="*60)
    print("jsonriver Python Benchmark")
    print("="*60 + "\n")

    await benchmark_file(
        comparisons,
        small_json,
        "a small file (64KiB)",
        1_000,  # Reduced from 10_000
    )

    await benchmark_file(
        comparisons,
        medium_json,
        "a medium file (1.4MiB)",
        100,  # Reduced from 1_000
    )

    await benchmark_file(
        comparisons,
        large_json,
        "a large file (25MiB)",
        10,  # Reduced from 20
    )

    print("="*60)
    print("Benchmark complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
