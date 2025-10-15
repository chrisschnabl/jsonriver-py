# jsonriver Benchmarks

This directory contains benchmarks for the Python implementation of jsonriver.

## Running the Benchmarks

```bash
python bench/python-bench.py
```

## Results

### Full File Parsing (python-bench.py)

Comparison of jsonriver vs json.loads when parsing complete files:

```
Parsing a small file (64KiB) averaged over 1000 runs
  jsonriver (Python)             9.233ms ±0.83ms
  json.loads                     0.262ms ±0.09ms

Parsing a medium file (1.4MiB) averaged over 100 runs
  jsonriver (Python)           229.585ms ±29.30ms
  json.loads                     5.826ms ±1.81ms

Parsing a large file (25MiB) averaged over 10 runs
  jsonriver (Python)          4526.521ms ±249.89ms
  json.loads                   118.702ms ±5.78ms
```

**Result**: `json.loads` is approximately **35-40x faster** than jsonriver for complete file parsing.

### Streaming Parsing (streaming-bench.py)

Comparison when data arrives in chunks (simulating network/streaming scenarios):

```
File size: 1446.3 KB, Chunk size: 1024 bytes, Chunks: 1447
Averaged over 100 runs

Total parsing time:
  jsonriver (streaming)     215.766ms ±7.93ms
  json.loads (buffered)       5.616ms ±0.35ms

Time to first value:
  jsonriver                   0.223ms ±0.02ms
  json.loads                  5.616ms ±0.35ms (must wait for all data)

  → jsonriver is 25.2x faster to first value!

Progressive updates:
  Updates received: 362
  Average time between updates: 0.578ms
  → User sees 362 progressive updates instead of waiting 209.4ms
```

**Result**: jsonriver provides **25x faster time-to-first-value** and **362 progressive updates** while json.loads must wait for complete data.

## Performance Characteristics

### When to Use jsonriver

jsonriver is designed for **streaming scenarios** where you want to:

1. **Start processing before data is complete**
   - Network requests where data arrives in chunks
   - Large files being read incrementally
   - Server-Sent Events (SSE)
   - Language model responses

2. **Provide progressive UI updates**
   - Show partial results as they arrive
   - Update progress indicators
   - Render incrementally

3. **Handle very large JSON**
   - Process data as it arrives
   - Avoid loading entire file into memory first

### When to Use json.loads

Use the standard library `json.loads` when:

1. **You have the complete JSON string already**
2. **Maximum performance is critical**
3. **You don't need incremental results**

## Performance Notes

The ~35x performance difference is expected and acceptable because:

1. **jsonriver is optimized for streaming**, not batch parsing
2. **json.loads is implemented in C** (highly optimized)
3. **Python's async overhead** adds latency
4. **Incremental results** have computational cost

The value proposition of jsonriver is **time-to-first-value** and **progressive updates**, not raw throughput.

## Comparison with TypeScript Implementation

The TypeScript jsonriver shows similar characteristics:
- Built-in `JSON.parse` is ~5x faster
- But jsonriver provides incremental parsing capability
- Trade-off is worth it for streaming scenarios

The Python implementation is relatively slower than TypeScript because:
- Python is generally slower than JavaScript V8
- json.loads is C-based (faster than JSON.parse)
- Python's async machinery has more overhead

## Test Data

The benchmarks use the same test files as the TypeScript implementation:

- `small-file.json`: 64 KiB
- `medium-file.json`: 1.4 MiB
- `large-file.json`: 25 MiB

These files are from the original [jsonriver](https://github.com/rictic/jsonriver) repository.

## License

Copyright (c) 2024 jsonriver-python contributors
SPDX-License-Identifier: BSD-3-Clause
