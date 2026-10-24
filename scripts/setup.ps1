# ReviewLens AI - Windows PowerShell Setup & Run Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         ReviewLens AI - Quick Setup & Launch            " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "`n[1/4] Checking Python environment..." -ForegroundColor Yellow
$PythonCmd = "python"
if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not found in PATH. Please install Python 3.9+." -ForegroundColor Red
    exit 1
}

Write-Host "[2/4] Installing backend dependencies..." -ForegroundColor Yellow
& $PythonCmd -m pip install -r "$ProjectRoot\backend\requirements.txt"

Write-Host "[3/4] Training Sentiment Analysis Model..." -ForegroundColor Yellow
& $PythonCmd "$ProjectRoot\backend\ml\train_model.py"

Write-Host "[4/4] Starting Flask REST API and Web App..." -ForegroundColor Green
Write-Host "Application is live at: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor DarkGray

& $PythonCmd "$ProjectRoot\backend\app.py"
