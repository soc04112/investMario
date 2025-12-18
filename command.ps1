function uvi {
    & "$PSScriptRoot\backend\myenv313\Scripts\Activate.ps1"

    Set-Location "$PSScriptRoot\backend"

    python -m uvicorn main:app --host 0.0.0.0 --port 8300 --reload

    Set-Location $PSScriptRoot
}

function react {
    Set-Location "$PSScriptRoot\frontend"
    npx vite
    Set-Location $PSScriptRoot
}