# Opens a visible window where Kimi Code works a task brief from docs/tasks/<Task>.md,
# streams its progress live, logs to logs/kimi-<Task>.log, then drops into an
# interactive Kimi session (same context) so the user can keep talking to it.
param(
    [Parameter(Mandatory = $true)][string]$Task,
    [switch]$Inner
)

$repo = Split-Path -Parent $PSScriptRoot
$brief = Join-Path $repo "docs\tasks\$Task.md"
if (-not (Test-Path $brief)) { Write-Error "No task brief at $brief"; exit 1 }

if (-not $Inner) {
    # Relaunch this script in a new, visible PowerShell window.
    Start-Process powershell -WorkingDirectory $repo -ArgumentList @(
        '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath, '-Task', $Task, '-Inner'
    )
    exit 0
}

$Host.UI.RawUI.WindowTitle = "Kimi Code - StudyForge $Task"
Set-Location $repo
New-Item -ItemType Directory -Force (Join-Path $repo 'logs') | Out-Null
$log = Join-Path $repo "logs\kimi-$Task.log"
Set-Content -Path $log -Value "=== $Task started $(Get-Date -Format s) ===" -Encoding UTF8

$prompt = "Read docs/tasks/$Task.md and complete that task fully. Follow DESIGN.md. Do not run git commit, git push, or switch branches."
Write-Host "Task: $Task" -ForegroundColor Cyan
Write-Host "Prompt: $prompt`n" -ForegroundColor DarkGray

function Show-Event($line) {
    try { $e = $line | ConvertFrom-Json -ErrorAction Stop } catch { Write-Host $line; return }
    $text = $null
    foreach ($k in 'text', 'content', 'message', 'delta', 'result') {
        if ($e.PSObject.Properties.Name -contains $k -and $e.$k -is [string]) { $text = $e.$k; break }
    }
    $tool = $null
    foreach ($k in 'tool', 'tool_name', 'name') {
        if ($e.PSObject.Properties.Name -contains $k -and $e.$k -is [string]) { $tool = $e.$k; break }
    }
    $type = if ($e.PSObject.Properties.Name -contains 'type') { $e.type } else { 'event' }
    if ($tool) { Write-Host "[$type] $tool" -ForegroundColor Yellow }
    if ($text) { Write-Host $text }
    if (-not $tool -and -not $text) {
        $s = $line; if ($s.Length -gt 300) { $s = $s.Substring(0, 300) + '...' }
        Write-Host "[$type] $s" -ForegroundColor DarkGray
    }
}

kimi -p $prompt --output-format stream-json 2>&1 | ForEach-Object {
    $l = "$_"
    Add-Content -Path $log -Value $l -Encoding UTF8
    Show-Event $l
}
$code = $LASTEXITCODE
Add-Content -Path $log -Value "=== $Task finished exit=$code $(Get-Date -Format s) ===" -Encoding UTF8

Write-Host "`n=== Kimi finished $Task (exit $code). Dropping into interactive session (same context). ===" -ForegroundColor Green
kimi -c -y
