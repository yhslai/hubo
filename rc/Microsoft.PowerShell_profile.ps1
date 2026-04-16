# Hardlink to $HOME\PowerShell\Microsoft.PowerShell_profile.ps1

Import-Module PSReadLine

$OnViModeChange = [scriptblock]{
    if ($args[0] -eq 'Command') {
        # Set the cursor to a blinking block.
        Write-Host -NoNewLine "`e[1 q"
    }
    else {
        # Set the cursor to a blinking line.
        Write-Host -NoNewLine "`e[5 q"
    }
}

Set-PsReadLineOption -EditMode Vi
Set-PSReadLineOption -ViModeIndicator Script -ViModeChangeHandler $OnViModeChange

# Shows navigable menu of all options when hitting Tab
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadlineKeyHandler -Key Ctrl+r -Function ReverseSearchHistory
Set-PSReadlineKeyHandler -Key Ctrl+s -Function ForwardSearchHistory
Set-PSReadlineKeyHandler -Key Ctrl+f -Function ForwardChar

$env:PATH += ";$HOME\github\little_windows\bin"
$env:PATH += ";$HOME\github\hubo\tools"
$env:PATH += ";$HOME\github\hubo\tools\third-party"
$env:PATH += ";C:\msys64\ucrt64\bin"

function global:prompt {
    $ESC = [char]27
    $loc = $executionContext.SessionState.Path.CurrentLocation

    $displayPath = $loc
    if ($loc.Provider.Name -eq "FileSystem") {
        $current = [System.IO.Path]::GetFullPath($loc.ProviderPath).TrimEnd('\')
        $homePath = [System.IO.Path]::GetFullPath($HOME).TrimEnd('\')

        if ($current.StartsWith($homePath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $relative = $current.Substring($homePath.Length).TrimStart('\')
            $displayPath = if ($relative) { "~\$relative" } else { "~" }
        }
    }

    $out = ""
    if ($loc.Provider.Name -eq "FileSystem") {
        $out += "$([char]27)]9;9;`"$($loc.ProviderPath)`"$([char]27)\"
    }
    $out += $displayPath

    return "$ESC[36m$out$('>' * ($nestedPromptLevel + 1)) $ESC[0m"
}


$env:PI_SKIP_VERSION_CHECK = "1"

# For pi
$env:EDITOR = "notepad"