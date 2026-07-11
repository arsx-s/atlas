param(
  [ValidateSet("windows", "macos")]
  [string]$Platform = $(if ($IsMacOS) { "macos" } else { "windows" }),
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")
$desktopRoot = Join-Path $repoRoot "apps\desktop"
$releaseRoot = Join-Path $repoRoot "release\desktop"
$platformReleaseRoot = Join-Path $releaseRoot $Platform
$desktopPackage = Get-Content (Join-Path $desktopRoot "package.json") -Raw | ConvertFrom-Json
$version = $desktopPackage.version

if ($Clean -and (Test-Path $platformReleaseRoot)) {
  Remove-Item -LiteralPath $platformReleaseRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $platformReleaseRoot -Force | Out-Null

Push-Location $repoRoot
try {
  if ($Platform -eq "windows") {
    & pnpm --dir apps/desktop dist:win
  } elseif ($Platform -eq "macos") {
    & pnpm --dir apps/desktop dist:mac
  } else {
    throw "Unsupported platform: $Platform"
  }

  if ($LASTEXITCODE -ne 0) {
    throw "Electron builder failed with exit code $LASTEXITCODE"
  }
} finally {
  Pop-Location
}

$artifactPaths = @()
if ($Platform -eq "windows") {
  $artifactPaths = Get-ChildItem -Path (Join-Path $desktopRoot "dist") -Filter "*.exe" -File -ErrorAction SilentlyContinue
} else {
  $artifactPaths = Get-ChildItem -Path (Join-Path $desktopRoot "dist") -Include "*.dmg","*.zip" -File -Recurse -ErrorAction SilentlyContinue
}

if (-not $artifactPaths -or $artifactPaths.Count -eq 0) {
  throw "No installer artifact was produced."
}

foreach ($artifact in $artifactPaths) {
  Copy-Item -LiteralPath $artifact.FullName -Destination (Join-Path $platformReleaseRoot $artifact.Name) -Force
}

Write-Host "Atlas installer build complete."
Write-Host "Version: $version"
Write-Host "Release folder: $platformReleaseRoot"
Get-ChildItem -Path $platformReleaseRoot | Select-Object Name,Length,LastWriteTime
