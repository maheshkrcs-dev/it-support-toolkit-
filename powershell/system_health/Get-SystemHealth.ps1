<#
.SYNOPSIS
  Read-only, basic Windows system health summary for IT support practice.
.DESCRIPTION
  Reports available CPU load, memory, system-drive space, uptime, and battery
  information. Individual checks fail independently so one unavailable CIM class
  does not prevent the rest of the report. Informational only; not a compliance test.
.NOTES
  Designed for Windows PowerShell 5.1+ and PowerShell 7 on Windows.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Write-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )
    Write-Output ('{0,-27} {1}' -f ($Name + ':'), $Value)
}

function Get-CimSafe {
    param(
        [Parameter(Mandatory = $true)][string]$ClassName,
        [string]$Filter
    )
    try {
        if ($Filter) {
            return Get-CimInstance -ClassName $ClassName -Filter $Filter -ErrorAction Stop
        }
        return Get-CimInstance -ClassName $ClassName -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Format-BatteryStatus {
    param([object]$Status)
    if ($null -eq $Status) { return 'Unavailable' }
    switch ([int]$Status) {
        1 { return 'Discharging' }
        2 { return 'Connected to AC' }
        3 { return 'Fully charged' }
        4 { return 'Low' }
        5 { return 'Critical' }
        6 { return 'Charging' }
        7 { return 'Charging (high)' }
        8 { return 'Charging (low)' }
        9 { return 'Charging (critical)' }
        10 { return 'Status undefined' }
        11 { return 'Partially charged' }
        default { return "Unknown status code ($Status)" }
    }
}

Write-Output 'IT Support Toolkit - Windows System Health'
Write-Output ('Generated: {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Output ('-' * 60)

# CPU: Win32_Processor.LoadPercentage is a CIM/WMI-reported value, not a live
# performance-counter sample. Report it as such and do not imply precision.
$processors = @(Get-CimSafe -ClassName 'Win32_Processor')
$cpuLoads = @($processors | Where-Object { $null -ne $_.LoadPercentage } |
    ForEach-Object { [double]$_.LoadPercentage })
if ($cpuLoads.Count -gt 0) {
    $cpuAverage = [math]::Round(($cpuLoads | Measure-Object -Average).Average, 0)
    Write-Check 'CPU load (CIM reported)' "$cpuAverage%"
} else {
    Write-Check 'CPU load' 'Unavailable'
}

$os = Get-CimSafe -ClassName 'Win32_OperatingSystem'
if ($null -ne $os) {
    $totalKb = [double]$os.TotalVisibleMemorySize
    $freeKb = [double]$os.FreePhysicalMemory
    if ($totalKb -gt 0 -and $freeKb -ge 0) {
        $usedPct = [math]::Round((($totalKb - $freeKb) / $totalKb) * 100, 1)
        $totalGb = [math]::Round($totalKb / 1MB, 2)
        $freeGb = [math]::Round($freeKb / 1MB, 2)
        Write-Check 'Memory total' "$totalGb GB"
        Write-Check 'Memory available' "$freeGb GB"
        Write-Check 'Memory used' "$usedPct%"
    } else {
        Write-Check 'Memory' 'Unavailable'
    }

    try {
        $lastBoot = [datetime]$os.LastBootUpTime
        if ($lastBoot -gt [datetime]::MinValue) {
            $uptime = (Get-Date) - $lastBoot
            Write-Check 'Uptime' ('{0} days, {1} hours' -f [math]::Floor($uptime.TotalDays), $uptime.Hours)
        } else {
            Write-Check 'Uptime' 'Unavailable'
        }
    } catch {
        Write-Check 'Uptime' 'Unavailable'
    }
} else {
    Write-Check 'Memory' 'Unavailable (OS query failed)'
    Write-Check 'Uptime' 'Unavailable (OS query failed)'
}

$systemDrive = $env:SystemDrive
if ([string]::IsNullOrWhiteSpace($systemDrive)) {
    Write-Check 'System drive' 'Unavailable'
} else {
    $escapedDrive = $systemDrive.Replace("'", "''")
    $drive = Get-CimSafe -ClassName 'Win32_LogicalDisk' -Filter "DeviceID='$escapedDrive'"
    if ($null -ne $drive -and [double]$drive.Size -gt 0 -and $null -ne $drive.FreeSpace) {
        $freePct = [math]::Round(([double]$drive.FreeSpace / [double]$drive.Size) * 100, 1)
        $freeGb = [math]::Round([double]$drive.FreeSpace / 1GB, 2)
        $totalGb = [math]::Round([double]$drive.Size / 1GB, 2)
        Write-Check "Drive $systemDrive free" "$freeGb GB of $totalGb GB ($freePct% free)"
    } else {
        Write-Check "Drive $systemDrive" 'Unavailable'
    }
}

$battery = @(Get-CimSafe -ClassName 'Win32_Battery' | Select-Object -First 1)
if ($battery.Count -gt 0 -and $null -ne $battery[0]) {
    Write-Check 'Battery status' (Format-BatteryStatus $battery[0].BatteryStatus)
    if ($null -ne $battery[0].EstimatedChargeRemaining) {
        Write-Check 'Battery charge' ("{0}%" -f $battery[0].EstimatedChargeRemaining)
    } else {
        Write-Check 'Battery charge' 'Unavailable'
    }
} else {
    Write-Check 'Battery' 'Not detected or unavailable (common on desktops)'
}

Write-Output ('-' * 60)
Write-Output 'Informational checks only; this is not a security/compliance certification.'
