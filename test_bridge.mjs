/**
 * Test bridge to verify Python tests against the Node.js jsonriver implementation
 *
 * This script allows Python tests to call the actual jsonriver implementation
 * to verify test expectations before implementing the Python version.
 */

import { parse } from 'jsonriver';

async function* makeStreamOfChunks(text, chunkSize) {
  for (let i = 0; i < text.length; i += chunkSize) {
    yield text.slice(i, i + chunkSize);
  }
}

async function parseJSON(jsonStr, chunkSize = 1) {
  const stream = makeStreamOfChunks(jsonStr, chunkSize);
  const results = [];

  try {
    for await (const value of parse(stream)) {
      // Use JSON serialization for easy transfer to Python
      results.push(JSON.stringify(value));
    }
    return { success: true, results };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Read command from stdin
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node test_bridge.mjs <json_string> [chunk_size]');
    process.exit(1);
  }

  const jsonStr = args[0];
  const chunkSize = args[1] ? parseInt(args[1], 10) : 1;

  const result = await parseJSON(jsonStr, chunkSize);
  console.log(JSON.stringify(result));
}

main().catch(err => {
  console.error(JSON.stringify({
    success: false,
    error: err.message
  }));
  process.exit(1);
});
