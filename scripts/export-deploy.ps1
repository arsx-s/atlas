<#
.SYNOPSIS
  Exports standalone deployment repositories for Atlas frontend and backend.
#>

function Write-FileNoBom {
  param([string]$Path, [string]$Value)
  $utf8 = New-Object System.Text.UTF8Encoding $false
  $parent = Split-Path $Path -Parent
  if (-not (Test-Path $parent)) { New-Item $parent -ItemType Directory -Force | Out-Null }
  [System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($Path), $Value, $utf8)
}

$ROOT = Split-Path -Parent $PSScriptRoot
$FRONTEND_SRC = Join-Path $ROOT "apps\web"
$BACKEND_SRC  = Join-Path $ROOT "backend"
$FRONTEND_DST = Join-Path $ROOT "deploy\frontend"
$BACKEND_DST  = Join-Path $ROOT "deploy\backend"

Write-Host "==> Cleaning deploy/" -ForegroundColor Cyan
if (Test-Path $FRONTEND_DST) { Remove-Item $FRONTEND_DST -Recurse -Force }
if (Test-Path $BACKEND_DST)  { Remove-Item $BACKEND_DST -Recurse -Force }
New-Item $FRONTEND_DST -ItemType Directory -Force | Out-Null
New-Item $BACKEND_DST -ItemType Directory -Force | Out-Null

Write-Host "==> Exporting frontend" -ForegroundColor Cyan
Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "vite.config.ts") -Destination (Join-Path $FRONTEND_DST "vite.config.ts")
Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "index.html") -Destination (Join-Path $FRONTEND_DST "index.html")
Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "README.md") -Destination (Join-Path $FRONTEND_DST "README.md")
Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "nginx.conf") -Destination (Join-Path $FRONTEND_DST "nginx.conf")
if (Test-Path (Join-Path $FRONTEND_SRC "public")) {
  Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "public") -Destination (Join-Path $FRONTEND_DST "public") -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $FRONTEND_SRC "src") -Destination (Join-Path $FRONTEND_DST "src") -Recurse -Force

Write-FileNoBom -Path (Join-Path $FRONTEND_DST "package.json") -Value @"
{
  "name": "atlas-frontend",
  "version": "0.1.0",
  "description": "Atlas web application.",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "6"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
"@

Write-FileNoBom -Path (Join-Path $FRONTEND_DST "tsconfig.json") -Value @"
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "useDefineForClassFields": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "types": ["vite/client"]
  },
  "include": ["src", "vite.config.ts"]
}
"@

Write-FileNoBom -Path (Join-Path $FRONTEND_DST ".gitignore") -Value @"
node_modules/
dist/
.env
.env.*
!.env.example
*.log
.DS_Store
Thumbs.db
"@

Write-Host "==> Exporting backend" -ForegroundColor Cyan
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "pyproject.toml") -Destination (Join-Path $BACKEND_DST "pyproject.toml")
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "requirements.txt") -Destination (Join-Path $BACKEND_DST "requirements.txt")
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "render.yaml") -Destination (Join-Path $BACKEND_DST "render.yaml")
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "README.md") -Destination (Join-Path $BACKEND_DST "README.md")
Get-ChildItem -LiteralPath (Join-Path $BACKEND_SRC "src") -Recurse -Force | Where-Object {
  $_.FullName -notmatch '__pycache__|\.pyc|\.egg-info' -and -not $_.PSIsContainer
} | ForEach-Object {
  $rel = $_.FullName.Substring($BACKEND_SRC.Length + 1)
  $target = Join-Path $BACKEND_DST $rel
  $parent = Split-Path $target -Parent
  if (-not (Test-Path $parent)) { New-Item $parent -ItemType Directory -Force | Out-Null }
  Copy-Item -LiteralPath $_.FullName -Destination $target -Force
}
$dbSrc = Join-Path $ROOT "database"
if (Test-Path $dbSrc) {
  Copy-Item -LiteralPath $dbSrc -Destination (Join-Path $BACKEND_DST "database") -Recurse -Force
}

Write-FileNoBom -Path (Join-Path $BACKEND_DST ".gitignore") -Value @"
__pycache__/
*.py[cod]
*.egg-info/
.env
.env.*
!.env.example
*.db
*.sqlite
.DS_Store
Thumbs.db
"@

$fc = (Get-ChildItem $FRONTEND_DST -Recurse -Force | Where-Object { -not $_.PSIsContainer }).Count
$bc = (Get-ChildItem $BACKEND_DST -Recurse -Force | Where-Object { -not $_.PSIsContainer }).Count
Write-Host "Done! Frontend: $fc files, Backend: $bc files" -ForegroundColor Green
