# Release Instructions for v0.0.1

## Status: Ready for Release

All code has been committed and pushed to GitHub:
- ✅ Version updated to 0.0.1
- ✅ All 37 tests passing
- ✅ Type checking passing (mypy --strict)
- ✅ README examples tested and working
- ✅ Code committed and pushed to main branch
- ✅ Git tag v0.0.1 created and pushed

## Next Step: Create GitHub Release

To trigger automatic publishing to PyPI via GitHub Actions:

### Option 1: Via GitHub Web UI (Easiest)

1. Go to: https://github.com/chrisschnabl/jsonriver-py/releases/new
2. Select tag: **v0.0.1**
3. Title: **v0.0.1 - Initial Release**
4. Description:
```markdown
# jsonriver v0.0.1 - Initial Release

This is the first release of jsonriver, a Python port of the TypeScript jsonriver library for streaming JSON parsing.

## Features

- **Incremental parsing**: Get progressively complete JSON values as data arrives
- **Zero dependencies**: Uses only Python standard library
- **Fully typed**: Complete type hints with mypy strict mode compliance
- **Memory efficient**: Reuses objects and arrays when possible
- **Correct**: Final result matches `json.loads()` exactly
- **Fast**: Optimized for performance with minimal overhead

## Installation

\`\`\`bash
pip install jsonriver
\`\`\`

Or with uv:
\`\`\`bash
uv add jsonriver
\`\`\`

## Testing

✅ 37/37 tests passing
✅ mypy --strict: 0 errors
✅ Cross-validated against TypeScript implementation

## Credits

This is a Python port of the excellent [jsonriver](https://github.com/rictic/jsonriver) TypeScript library by Peter Burns (@rictic).

- Original TypeScript: Copyright (c) 2023 Google LLC
- Python Port: Copyright (c) 2024 jsonriver-python contributors

Licensed under BSD-3-Clause
```

5. Click **Publish release**

### Option 2: Trigger Workflow Manually

If you want to publish without creating a release:

1. Go to: https://github.com/chrisschnabl/jsonriver-py/actions/workflows/workflow.yml
2. Click **Run workflow**
3. Select branch: **main**
4. Click **Run workflow**

### Option 3: Manual Publishing (Backup)

If GitHub Actions doesn't work:

```bash
cd /Users/chris/streamjson
uv build
uv publish --token <YOUR_PYPI_TOKEN>
```

## What Happens Next

Once you create the GitHub release:

1. GitHub Actions workflow will automatically trigger
2. The workflow will:
   - Check out the code
   - Set up Python and uv
   - Build the package (jsonriver-0.0.1.tar.gz and .whl)
   - Publish to PyPI using your API token

3. Within a few minutes, the package will be live at:
   - https://pypi.org/project/jsonriver/0.0.1/

## Verification

After publishing, verify the package:

```bash
# Install from PyPI
pip install jsonriver==0.0.1

# Test it works
python -c "from jsonriver import parse; print('✅ Installation successful!')"
```

## GitHub Repository

- Repository: https://github.com/chrisschnabl/jsonriver-py
- Releases: https://github.com/chrisschnabl/jsonriver-py/releases
- Actions: https://github.com/chrisschnabl/jsonriver-py/actions

---

**All preparation work is complete!** 🎉

Just create the GitHub release and the automation will handle the rest.
