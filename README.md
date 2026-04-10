## Dependencies

`python` and `pip` should be installed. (Recommended: [uv](https://docs.astral.sh/uv/getting-started/installation/))

```powershell
uv pip install -r requirements.txt
```

`tools` and `tools/third-party` directories of this repo should be in your `$PATH`.

## Python Tools

```powershell
run_script <script_name> [args...]
```

This script will execute Python or Node.js scripts in the `tools` directory. It knows to activate the venv first. But if you're developing the Python scripts separately, you might need to first:

```powershell
.\.venv\scripts\activate
run_script <script_name> [args...]
```

or directly:

```bash
./.venv/bin/python <script_path> [args...]
```