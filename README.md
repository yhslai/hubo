## Dependencies

`python` and `pip` should be installed. (Recommended: [uv](https://docs.astral.sh/uv/getting-started/installation/))

```powershell
uv pip install -r requirements.txt
```

`tools` and `tools/third-party` directories of this repo should be in your `$PATH`.

## One-Shot Scripts

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

## Local Tools and Configuration

- `tools/ahk/general.ahk` - AutoHotkey v2 keyboard remappings.
- `tools/clean_backups_and_ds.py` - Recursively removes Blender backups, `.kra~`, and `.DS_Store` files from the current directory. Use `run_script clean_backups_and_ds --dry-run` to preview.
- `tools/images_to_pdf.py` - Converts images in a directory to a PDF. Requires ImageMagick's `magick` command as well as the Python dependencies.
- `tools/restart_wacom_driver.ps1` - Restarts the Wacom driver service using `gsudo`.
- `tools/f3d.bat` - Runs F3D from its default installation path.

## Other Programs

- `VideoDownloader/` - A Chrome/Edge extension that downloads videos from Youtube, Reddit, RedGIF, XVideo, and Streamtape, with extra domains/URLs (e.g. Pornhub) configurable in `video_downloader.yaml`. It has a Proxy and a Downloader service as backend.