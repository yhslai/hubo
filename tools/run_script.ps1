<#
.SYNOPSIS
    A generic script runner for Python and Node.js.

.DESCRIPTION
    This script finds and executes .py or .js scripts located in its own directory.
    - When run with a script name, it executes that script, passing along any additional arguments.
    - When run without any arguments, it lists all available scripts.

.EXAMPLE
    # List all available scripts
    run

.EXAMPLE
    # Run the clean_backups.py script with a --dry-run flag
    run clean_backups --dry-run
#>

# The '$PSScriptRoot' variable is an automatic variable that contains the
# full path to the directory where the script file is located.
$scriptsDirectory = $PSScriptRoot

$pythonPath = "$scriptsDirectory\..\.venv\Scripts\python.exe"

# --- Main Logic: Check if any arguments were provided ---

if ($args.Count -eq 0) {
    #
    # === No arguments: List available scripts ===
    #
    Write-Host "Available scripts in '$scriptsDirectory':"

    # Get all .py and .js files, select their name without extension (BaseName),
    # sort them, and ensure the list is unique.
    $availableScripts = Get-ChildItem -Path $scriptsDirectory -Recurse -Include *.py, *.js |
                        Select-Object -ExpandProperty BaseName |
                        Sort-Object -Unique

    if ($availableScripts) {
        foreach ($script in $availableScripts) {
            Write-Host "  $script"
        }
        Write-Host "`nUsage: run <script_name> [args...]"
    } else {
        Write-Host "  (No .py or .js scripts found)"
    }
    
    # Exit cleanly
    exit 0
}
else {
    #
    # === Arguments provided: Run the specified script ===
    #
    $scriptName = $args[0]
    $remainingArgs = $args | Select-Object -Skip 1

    # Construct the full paths for the potential scripts
    $pyScriptPath = Join-Path $scriptsDirectory "$scriptName.py"
    $jsScriptPath = Join-Path $scriptsDirectory "$scriptName.js"

    # Check for the Python script first, then Node.js
    if (Test-Path $pyScriptPath) {
        # Use the call operator '&' to execute the command.
        # PowerShell will correctly pass the array of $remainingArgs as individual arguments.
        & $pythonPath $pyScriptPath $remainingArgs
    }
    elseif (Test-Path $jsScriptPath) {
        & node $jsScriptPath $remainingArgs
    }
    else {
        # If neither script was found, show an informative error.
        Write-Error "Error: Script '$scriptName.py' or '$scriptName.js' not found."
        exit 1
    }
}