param([string]$Python = 'python', [string]$InnoCompiler = $env:ISCC)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not $InnoCompiler) {
    $candidates = @('.\.build-tools\InnoSetup\ISCC.exe', "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe")
    $InnoCompiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $InnoCompiler) { throw 'Install Inno Setup 6.7.3 and pass -InnoCompiler or set ISCC.' }
& $Python packaging/create_icon.py
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
& $Python -m unittest -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; no installer will be built' }
& $Python -m PyInstaller --noconfirm --windowed --onedir --name LanGo --icon assets/lango.ico --add-data 'assets/lango.ico:assets' --add-data 'assets/detective.png:assets' lango_app.py
if ($LASTEXITCODE -ne 0) { throw 'Application build failed' }
& $InnoCompiler /Q packaging/LanGo.iss
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
$installer = Get-Item release/LanGo-Setup-1.3.6-Windows-x64.exe
$checksum = (Get-FileHash -LiteralPath $installer.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
"$checksum  $($installer.Name)" | Set-Content -Encoding ascii release/SHA256SUMS.txt
Write-Output "Built $($installer.Name); SHA-256 $checksum"




