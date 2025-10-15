# Publishing jsonriver to PyPI

This guide explains how to publish the jsonriver package to PyPI using `uv`.

## Prerequisites

1. **Install uv**: Follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
2. **PyPI Account**: Create an account at [pypi.org](https://pypi.org)
3. **PyPI API Token**: Generate an API token from your PyPI account settings

## Publishing Methods

### Method 1: Local Publishing (Manual)

1. **Build the package**:
   ```bash
   uv build
   ```
   This creates distribution files in the `dist/` directory.

2. **Publish to PyPI**:
   ```bash
   uv publish --token YOUR_PYPI_TOKEN
   ```

   Or set the token as an environment variable:
   ```bash
   export UV_PUBLISH_TOKEN=YOUR_PYPI_TOKEN
   uv publish
   ```

### Method 2: GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically publishes to PyPI when you create a release.

#### Setup:

1. **Add PyPI API token to GitHub Secrets**:
   - Go to your repository settings → Secrets and variables → Actions
   - Add a new secret named `PYPI_API_TOKEN`
   - Paste your PyPI API token as the value

2. **Create a release**:
   ```bash
   # Tag the release
   git tag v1.0.0
   git push origin v1.0.0

   # Create release on GitHub
   # Go to GitHub → Releases → Create new release
   # Select the tag v1.0.0
   # Publish the release
   ```

3. **Automatic publishing**:
   The workflow will automatically build and publish the package to PyPI.

### Method 3: Using Trusted Publishers (Most Secure)

PyPI supports [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) for GitHub Actions, which doesn't require storing tokens.

1. **Register Trusted Publisher on PyPI**:
   - Go to your PyPI project settings
   - Add GitHub as a trusted publisher
   - Enter: Repository owner, name, workflow filename, environment name

2. **Update workflow**: The existing `.github/workflows/publish.yml` already uses `id-token: write` for trusted publishing.

3. **No token needed**: The workflow will authenticate automatically via OIDC.

## Testing on TestPyPI

Before publishing to PyPI, test on TestPyPI:

1. **Add TestPyPI index** to `pyproject.toml`:
   ```toml
   [[tool.uv.index]]
   name = "testpypi"
   url = "https://test.pypi.org/simple/"
   publish-url = "https://test.pypi.org/legacy/"
   explicit = true
   ```

2. **Publish to TestPyPI**:
   ```bash
   uv publish --index testpypi --token YOUR_TESTPYPI_TOKEN
   ```

3. **Install from TestPyPI**:
   ```bash
   uv pip install --index-url https://test.pypi.org/simple/ jsonriver
   ```

## Version Management

Update the version in `pyproject.toml` before publishing:

```toml
[project]
name = "jsonriver"
version = "1.0.1"  # Update this
```

Follow [Semantic Versioning](https://semver.org/):
- Major version (1.x.x): Breaking changes
- Minor version (x.1.x): New features, backward compatible
- Patch version (x.x.1): Bug fixes, backward compatible

## Pre-publish Checklist

Before publishing, ensure:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Type checking passes: `mypy src/jsonriver --strict`
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG updated with new version
- [ ] README.md is accurate
- [ ] LICENSE file is correct
- [ ] Build succeeds: `uv build`
- [ ] Package installs: `uv pip install dist/*.whl`

## Troubleshooting

### Build fails

```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info/

# Rebuild
uv build
```

### Upload fails mid-way

If some files uploaded but others failed, uv will skip existing files:

```bash
# Retry - existing files will be skipped
uv publish --token YOUR_TOKEN
```

### Version already exists

PyPI doesn't allow overwriting existing versions. Increment the version number and rebuild:

```bash
# Update version in pyproject.toml
# Then rebuild and publish
uv build
uv publish --token YOUR_TOKEN
```

## Resources

- [uv Publishing Documentation](https://docs.astral.sh/uv/guides/package/#publishing-your-package)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions Publishing Guide](https://docs.astral.sh/uv/guides/integration/github/#publishing-to-pypi)
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
