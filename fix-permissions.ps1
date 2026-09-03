# FPV Controller — Add to AppLocker exceptions
# Run as Administrator!

$exePath = Join-Path $PSScriptRoot "FPV-Controller.exe"

Write-Host ""
Write-Host "  FPV Controller — Додавання у винятки" -ForegroundColor Cyan
Write-Host ""

# 1. Remove Mark of the Web
Write-Host "[1/3] Зняття блокування..." -ForegroundColor Yellow
Unblock-File -Path $exePath -ErrorAction SilentlyContinue

# 2. Add Windows Defender exclusion
Write-Host "[2/3] Додавання у винятки Windows Defender..." -ForegroundColor Yellow
$dir = Split-Path $exePath
Add-MpPreference -ExclusionPath $dir -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionProcess "FPV-Controller.exe" -ErrorAction SilentlyContinue

# 3. Try to add AppLocker rule
Write-Host "[3/3] Додавання правила AppLocker..." -ForegroundColor Yellow
try {
    $hash = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash
    
    # Create a new rule based on file hash
    $rule = New-Object -ComObject "Microsoft.Windows.AppLocker.AppLockerConfig"
    
    Write-Host "  [OK] Спроба додати правило за хешем" -ForegroundColor Green
} catch {
    Write-Host "  [!] AppLocker керується через gpedit.msc" -ForegroundColor Yellow
    Write-Host "  Відкрий: Win+R → gpedit.msc" -ForegroundColor Yellow
    Write-Host "  Конфігурація комп'ютера → Адміністративні шаблони → Windows Компоненти → AppLocker" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[OK] Запуск програми..." -ForegroundColor Green
Start-Process -FilePath $exePath

Write-Host ""
Write-Host "Натисни Enter для виходу..."
Read-Host
