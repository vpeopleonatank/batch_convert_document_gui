param(
  [string]$PythonExe = "python",
  [string[]]$PythonArgs = @(),
  [string]$Arch = "x64",
  [switch]$RecreateVenv,
  [string]$LibreOfficeMsiPath = "",
  [string]$LibreOfficeMsiUrl = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$VenvDir = Join-Path $ProjectRoot ".venv"
$Spec = Join-Path $ProjectRoot "packaging/pyinstaller/batch-doc-to-docx-gui.spec"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$AppName = "batch-doc-to-docx-gui"
$ZipPath = Join-Path $DistDir "$AppName-windows-$Arch.zip"

Write-Host "==> Project: $ProjectRoot"
Write-Host "==> Python:  $PythonExe $PythonArgs"

if (-not (Test-Path $Spec)) {
  throw "Missing spec: $Spec"
}

if ($RecreateVenv -and (Test-Path $VenvDir)) {
  Write-Host "==> Recreate venv: $VenvDir"
  Remove-Item -Recurse -Force $VenvDir
}

if (-not (Test-Path $VenvDir)) {
  Write-Host "==> Create venv: $VenvDir"
  & $PythonExe @PythonArgs -m venv $VenvDir
} else {
  Write-Host "==> Reuse venv: $VenvDir"
}

$VenvPython = Join-Path $VenvDir "Scripts/python.exe"
if (-not (Test-Path $VenvPython)) {
  throw "Missing venv python: $VenvPython"
}

Write-Host "==> Install deps"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install . pyinstaller

Write-Host "==> Build (PyInstaller)"
& $VenvPython -m PyInstaller --noconfirm --clean $Spec

if (-not (Test-Path $DistDir)) {
  throw "Missing dist dir: $DistDir"
}

$AppDistDir = Join-Path $DistDir $AppName
if (-not (Test-Path $AppDistDir)) {
  throw "Missing app dist dir: $AppDistDir"
}

function Resolve-LibreOfficeMsi {
  param(
    [string]$MsiPath,
    [string]$MsiUrl
  )

  if (-not [string]::IsNullOrWhiteSpace($MsiPath)) {
    $Candidate = Resolve-Path $MsiPath
    return $Candidate.Path
  }

  if (-not [string]::IsNullOrWhiteSpace($MsiUrl)) {
    $LoDir = Join-Path $BuildDir "libreoffice"
    New-Item -ItemType Directory -Force -Path $LoDir | Out-Null
    $DownloadPath = Join-Path $LoDir "LibreOffice.msi"
    Write-Host "==> Download LibreOffice MSI"
    Write-Host "URL: $MsiUrl"
    Invoke-WebRequest -Uri $MsiUrl -OutFile $DownloadPath
    return $DownloadPath
  }

  return $null
}

function Bundle-LibreOffice {
  param(
    [string]$MsiPath,
    [string]$AppDir
  )

  $ExtractDir = Join-Path $BuildDir "libreoffice-extract"
  if (Test-Path $ExtractDir) {
    Remove-Item -Recurse -Force $ExtractDir
  }
  New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null

  Write-Host "==> Extract LibreOffice (admin install)"
  $Args = @("/a", $MsiPath, "/qn", "TARGETDIR=$ExtractDir")
  $Proc = Start-Process -FilePath "msiexec.exe" -ArgumentList $Args -Wait -PassThru
  if ($Proc.ExitCode -ne 0) {
    throw "LibreOffice MSI extraction failed (msiexec exit $($Proc.ExitCode))."
  }

  $Soffice = Get-ChildItem -Path $ExtractDir -Recurse -File -Filter "soffice.exe" |
    Where-Object { $_.FullName -match "\\\\program\\\\soffice\\.exe$" } |
    Select-Object -First 1

  if (-not $Soffice) {
    throw "Could not locate program\\soffice.exe in extracted LibreOffice."
  }

  $LoRoot = $Soffice.Directory.Parent.FullName
  $Target = Join-Path $AppDir "LibreOffice"

  if (Test-Path $Target) {
    Remove-Item -Recurse -Force $Target
  }
  New-Item -ItemType Directory -Force -Path $Target | Out-Null

  Write-Host "==> Bundle LibreOffice into: $Target"
  Copy-Item -Path (Join-Path $LoRoot "*") -Destination $Target -Recurse -Force

  $BundledSoffice = Join-Path $Target "program\\soffice.exe"
  if (-not (Test-Path $BundledSoffice)) {
    throw "Bundled LibreOffice is missing expected soffice path: $BundledSoffice"
  }
}

$LoMsi = Resolve-LibreOfficeMsi -MsiPath $LibreOfficeMsiPath -MsiUrl $LibreOfficeMsiUrl
if ($LoMsi) {
  Bundle-LibreOffice -MsiPath $LoMsi -AppDir $AppDistDir
}

if (Test-Path $ZipPath) {
  Remove-Item -Force $ZipPath
}

Write-Host "==> Zip: $ZipPath"
Compress-Archive -Path (Join-Path $AppDistDir "*") -DestinationPath $ZipPath -Force

Write-Host "==> Done"
Write-Host "Build output: $DistDir\\$AppName\\"
Write-Host "Zip output:   $ZipPath"
