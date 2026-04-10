Create a script called `path_linker`. It takes `pathLinker.binPath` from `config.json`. The purpose of this script is to symlink some binary executables to `binPath` so they can be run by command line directly. Note that we assume `toolPath` is already in `$PATH` and `path_linker` should never update `$PATH` directly.

`path_linker` is aware of some applications, like Houdini, and knows how to handle their versioning.

# Examples

```
path_linker houdini 20.5.654
path_linker houdini latest
path_linker git-bash
```

# Details

`path_linker` will create some symlinks in `binPath`. For example, in Houdini's case it creates several:

- `{toolPath}/{binName}.exe` -> `C:\Program Files\Side Effects Software\Houdini {houdiniVersion}\bin\{binName}.exe`

for each `binName` (by default they are `[houdini, hcmd, mplay, hython]`). `houdiniVersion` is either specified by command argument directly or the latest version number found by iterating over `Side Effects Software`'s subdirectories.

If a file with the same name exists, check if it's a symlink to an executable from the same app (might be a different version). If so, overwrite it and log that we upgraded / downgraded the version. If it's an unrelated file or a symlink to a different app, log a warning and leave it alone.

If the version argument is absent, it means that app's path is usually not versioned (e.g. `C:\Program Files\Git\bin\bash.exe').

# Implementation Plan

## S0: Just do it

Since this is a relatively simple tool, we just do it in one run. For now we only need to support two third-party tools, `git` and `houdini`. `toolPath` should be hardcoded as `tools/third-party` in this repo's home dir.

When called without arguments, print usage.

# Done Notes

Implemented in `tools/path_linker.py`.

- Added CLI with supported apps: `houdini`, `git-bash` (and `git` alias for git-bash).
- Added Houdini version resolution logic:
  - Accepts explicit version or `latest`.
  - Detects latest installed version under `C:\Program Files\Side Effects Software` by parsing `Houdini <version>` directories.
- Added link creation/replacement behavior for Houdini executables (`houdini`, `hcmd`, `mplay`, `hython`) and `git-bash.exe`.
- Added safety checks before overwriting existing files:
  - Replaces only when the existing entry is a symlink that points to the same app.
  - Warns and skips when target is unrelated or a regular file.
- Added upgrade/downgrade messaging when replacing Houdini symlinks across versions.
- Added usage + examples output when called without args, and error handling for unsupported apps or symlink permission issues on Windows.