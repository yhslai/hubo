# PowerShell cmdlet to Restart the Wacom Drvier


$srvName = "WTabletServicePro"
$servicePrior = Get-Service $srvName
"$srvName is now " + $servicePrior.status
$cmd = @"
Set-Service ${srvName} -startuptype manual
Restart-Service ${srvName}
"@
gsudo $cmd
$serviceAfter = Get-Service $srvName
"$srvName is now " + $serviceAfter.status
