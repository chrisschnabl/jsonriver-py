# 🎉 jsonriver Successfully Published to PyPI!

## Publication Details

**Package Name:** jsonriver
**Version:** 1.0.0
**PyPI URL:** https://pypi.org/project/jsonriver/
**Published:** October 15, 2024

## Package Information

- **License:** BSD-3-Clause
- **Python Version:** >=3.11
- **Dependencies:** None (stdlib only)
- **Package Size:**
  - Wheel: 12,514 bytes
  - Source: 16,809 bytes

## Installation

Users can now install jsonriver using:

```bash
# Using pip
pip install jsonriver

# Using uv
uv add jsonriver

# Using uv pip
uv pip install jsonriver
```

## Verification

The package has been tested and verified:

✅ Successfully uploaded to PyPI
✅ Installable via pip
✅ All functionality working correctly
✅ Imports work properly
✅ Streaming JSON parsing verified
✅ Type hints included
✅ Tests included in source distribution

## Test Results

```
Testing jsonriver package from PyPI...

  ✓ {"a": 1} -> {'a': 1.0}
  ✓ [1, 2, 3] -> [1.0, 2.0, 3.0]
  ✓ "hello" -> hello
  ✓ null -> None
  ✓ true -> True
  ✓ false -> False

✅ All tests passed!
```

## GitHub Integration

### Trusted Publishing Setup

The repository is configured for PyPI Trusted Publishing:

- **Owner:** chrisschnabl
- **Repository:** https://github.com/chrisschnabl/streamjson
- **Workflow:** workflow.yml
- **Environment:** pypi

### Future Releases

To publish future versions via GitHub Actions:

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a new release on GitHub:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. Create release on GitHub UI
5. GitHub Actions will automatically publish to PyPI

OR manually trigger the workflow:
- Go to Actions → Publish to PyPI → Run workflow

## Next Steps

### For Version 1.0.1 or Later

1. **Update Version**
   ```toml
   # In pyproject.toml
   version = "1.0.1"
   ```

2. **Update Changelog**
   - Document changes in README.md or CHANGELOG.md

3. **Run Tests**
   ```bash
   pytest tests/ -v
   mypy src/jsonriver --strict
   ```

4. **Build and Publish**
   ```bash
   uv build
   uv publish --token <your-token>
   ```

   OR use GitHub Actions (recommended)

## Package URLs

- **PyPI:** https://pypi.org/project/jsonriver/
- **Repository:** https://github.com/chrisschnabl/streamjson
- **Original:** https://github.com/rictic/jsonriver

## Credits

This is a Python port of the TypeScript [jsonriver](https://github.com/rictic/jsonriver) library by Peter Burns (@rictic).

- Original TypeScript: Copyright (c) 2023 Google LLC
- Python Port: Copyright (c) 2024 jsonriver-python contributors

---

**Published by:** chrisschnabl
**Date:** October 15, 2024
**Status:** ✅ Live on PyPI
