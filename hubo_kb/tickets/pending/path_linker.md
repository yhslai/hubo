Create a script called `path_linker`. It takes `pathLinker.binPath` from `config.json`. The purpose of this script is to symlink some binary executables to `binPath` so they can be run by command line directly. Note that we assume `binPath` is already in `$PATH` and `path_linker` should never update `$PATH` directly.

`path_linker` is aware of some applications, like Houdini, and knows how to handle their versioning.

# Examples

```
path_linker houdini 20.5.654
path_linker houdini latest
path_linker git-bash
```

# Details

`path_linker` will create some symlinks in `binPath`. For example, in Houdini's case it creates several:

- `{binPath}/{binName}.exe` -> `C:\Program Files\Side Effects Software\Houdini {houdiniVersion}\bin\{binName}.exe`

for each `binName` (by default they are `[houdini, hcmd, mplay, hyphon]`). `houdiniVersion` is either specified by command argument directly or the latest version number found by iterating over `Side Effects Software`'s subdirectories.

If a file with the same name exists, check if it's a symlink to an executable from the same app (might be a different version). If so, overwrite it and log that we upgraded / downgraded the version. If it's an unrelated file or a symlink to a different app, log a warning and leave it alone.

If the version argument is absent, it means that app's path is usually not versioned (e.g. `C:\Program Files\Git\bin\bash.exe').