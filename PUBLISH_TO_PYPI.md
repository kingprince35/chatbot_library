# How to publish to PyPI (step by step)

## 0. One-time setup
1. Create an account at https://pypi.org/account/register/ and enable 2FA.
2. Create an account at https://test.pypi.org (separate account) for practice uploads.
3. Create an API token: Account settings -> API tokens -> "Add API token" (scope: entire account
   for the first upload). Copy it (starts with `pypi-`). You see it only once.

## 1. Edit before publishing
- `pyproject.toml`: change `name` if taken (check https://pypi.org/project/YOUR-NAME/ -> 404 = free),
  set `authors`, and the `Homepage` URL.
- `LICENSE`: put your name.
- If you rename the package, rename the folder `src/groq_gemini_bridge` and fix imports.

## 2. Test locally
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## 3. Build
```bash
rm -rf dist
python -m build                    # creates dist/*.whl and dist/*.tar.gz
twine check dist/*                 # must say PASSED
```

## 4. Practice upload to TestPyPI (recommended)
```bash
twine upload --repository testpypi dist/*
# username: __token__     password: your TestPyPI token
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple groq-gemini-bridge
```

## 5. Real upload
```bash
twine upload dist/*
# username: __token__     password: your PyPI token
```
Now anyone can run: `pip install groq-gemini-bridge`

## 6. Releasing a new version
PyPI never allows re-uploading the same version. To update:
1. Change `version` in `pyproject.toml` (and `__version__` in `__init__.py`), e.g. 0.1.1
2. `rm -rf dist && python -m build && twine upload dist/*`

## Tips
- Save the token in `~/.pypirc` so you don't type it every time:
  ```
  [pypi]
  username = __token__
  password = pypi-XXXX
  ```
- Never commit tokens or `.env` to git.
- Later, switch to "Trusted Publishing" with GitHub Actions (no token needed).
