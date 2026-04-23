# Setup script for DreamsLIVE_Solutions-ServiceAgent

# Set Execution Policy for the current process to allow running the setup
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

Write-Host "Setting up virtual environment..." -ForegroundColor Cyan
python -m venv .venv

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`nSetup complete! To activate the environment in the future, run:" -ForegroundColor Green
Write-Host ".\.venv\Scripts\Activate.ps1"
