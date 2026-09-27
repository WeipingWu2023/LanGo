param([string]$Python = 'python', [string]$InnoCompiler = $env:ISCC)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not $InnoCompiler) {
    $candidates = @('.\.build-tools\InnoSetup\ISCC.exe', "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe")
    $InnoCompiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $InnoCompiler) { throw 'Install Inno Setup 6.7.3 and pass -InnoCompiler or set ISCC.' }
& $Python packaging/fetch_data.py
if ($LASTEXITCODE -ne 0) { throw 'Dictionary source verification failed' }
& $Python packaging/build_dictionary.py
if ($LASTEXITCODE -ne 0) { throw 'Dictionary generation failed' }
& $Python packaging/create_icon.py
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
& $Python -m unittest -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; no installer will be built' }
& $Python -m PyInstaller --noconfirm --windowed --onedir --name Wordroom --icon assets/wordroom.ico --add-data 'starter.json:.' --add-data 'assets/wordroom.ico:assets' --add-data 'data/dictionary.db:data' dictionary.py
if ($LASTEXITCODE -ne 0) { throw 'Application build failed' }
& $InnoCompiler /Q packaging/Wordroom.iss
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
$installer = Get-Item release/Wordroom-Setup-1.2.0-Windows-x64.exe
$checksum = (Get-FileHash -LiteralPath $installer.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
"$checksum  $($installer.Name)" | Set-Content -Encoding ascii release/SHA256SUMS.txt
Write-Output "Built $($installer.Name); SHA-256 $checksum"
