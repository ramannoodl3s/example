$env:OLLAMA_FLASH_ATTENTION = "1"
$env:OLLAMA_KV_CACHE_TYPE = "q8_0"

$ollamaRunning = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaRunning) {
    Write-Host "Starting Ollama..."
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
} else {
    Write-Host "Ollama is already running."
    Write-Warning "OLLAMA_FLASH_ATTENTION / OLLAMA_KV_CACHE_TYPE are not applied to the running Ollama process. Quit Ollama from the system tray and re-run this script, or set them permanently as user environment variables, e.g.: [Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION', '1', 'User')"
}

$server = Start-Process uv -ArgumentList "run", "studyforge", "serve" -PassThru
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 1
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($ready) {
    Start-Process "http://127.0.0.1:8000"
} else {
    Write-Warning "Server did not become healthy within 20 seconds; not opening the browser."
}
Wait-Process -Id $server.Id
