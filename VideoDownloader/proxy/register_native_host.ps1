param(
    [Parameter(Mandatory = $true)]
    [string]$ExtensionId
)

$ErrorActionPreference = 'Stop'

$HostName = 'com.hubo.video_downloader.proxy'

if ([string]::IsNullOrWhiteSpace($ExtensionId)) {
    throw 'ExtensionId cannot be empty.'
}

$proxyDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templatePath = Join-Path $proxyDir 'native-messaging-host.template.json'
$manifestPath = Join-Path $proxyDir 'native-messaging-host.json'
$hostPath = Join-Path $proxyDir 'proxy_host.cmd'

if (-not (Test-Path $templatePath)) {
    throw "Template not found: $templatePath"
}

if (-not (Test-Path $hostPath)) {
    throw "Host launcher not found: $hostPath"
}

$template = Get-Content -Raw -Path $templatePath
$manifestJson = $template.Replace('__HOST_PATH__', ($hostPath -replace '\\', '\\\\'))
$manifestJson = $manifestJson.Replace('__EXTENSION_ID__', $ExtensionId)

Set-Content -Path $manifestPath -Value $manifestJson -Encoding UTF8

$chromeKey = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\$HostName"
$edgeKey = "HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\$HostName"

New-Item -Path $chromeKey -Force | Out-Null
New-ItemProperty -Path $chromeKey -Name '(Default)' -PropertyType String -Value $manifestPath -Force | Out-Null

New-Item -Path $edgeKey -Force | Out-Null
New-ItemProperty -Path $edgeKey -Name '(Default)' -PropertyType String -Value $manifestPath -Force | Out-Null

Write-Host "Wrote native host manifest: $manifestPath"
Write-Host "Extension ID in manifest: $ExtensionId"
Write-Host "Registered for Chrome: $chromeKey"
Write-Host "Registered for Edge:   $edgeKey"
