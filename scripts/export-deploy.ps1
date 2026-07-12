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

Write-FileNoBom -Path (Join-Path $FRONTEND_DST ".env.example") -Value @"
# VITE_ATLAS_API_BASE_URL=https://your-backend.onrender.com/api/v1
"@

Write-Host "==> Exporting backend" -ForegroundColor Cyan
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "pyproject.toml") -Destination (Join-Path $BACKEND_DST "pyproject.toml")
Copy-Item -LiteralPath (Join-Path $BACKEND_SRC "requirements.txt") -Destination (Join-Path $BACKEND_DST "requirements.txt")

Write-FileNoBom -Path (Join-Path $BACKEND_DST "render.yaml") -Value @"
services:
  - type: web
    name: atlas-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn atlas_backend.main:app --host 0.0.0.0 --port `$PORT --workers 2 --proxy-headers --forwarded-allow-ips "*"
    healthCheckPath: /api/v1/health
    envVars:
      - key: PYTHONPATH
        value: /opt/render/project/src/src
      - key: ATLAS_ENV
        value: production
      - key: ATLAS_RUNTIME_MODE
        value: hybrid
      - key: ATLAS_API_BASE_PATH
        value: /api/v1
      - key: ATLAS_HTTPS_ONLY
        value: "true"
      - key: ATLAS_LOG_LEVEL
        value: info
      - key: ATLAS_LOCAL_MODE_ENABLED
        value: "false"
      - key: ATLAS_LOCAL_MODELS_ENABLED
        value: "false"
      - key: ATLAS_CLOUD_SYNC_ENABLED
        value: "false"
      - key: ATLAS_KNOWLEDGE_GRAPH_ENABLED
        value: "false"
      - key: ATLAS_SQLITE_PATH
        value: /var/data/atlas.db
      - key: ATLAS_DOCUMENTS_PATH
        value: /var/data/documents
      - key: ATLAS_STORAGE_PATH
        value: /var/data/storage
      - key: ATLAS_STORAGE_TYPE
        value: filesystem
      - key: ATLAS_OCR_PROVIDER
        value: tesseract
      - key: ATLAS_CHUNKING_STRATEGY
        value: semantic
      - key: ATLAS_MAX_DOCUMENT_SIZE_MB
        value: "100"
      - key: ATLAS_RATE_LIMIT_ENABLED
        value: "true"
      - key: ATLAS_JWT_SECRET
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: BRAVE_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: NEO4J_URL
        sync: false
      - key: AWS_S3_BUCKET
        sync: false
      - key: AWS_ACCESS_KEY_ID
        sync: false
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: ATLAS_CORS_ALLOWED_ORIGINS
        value: https://your-frontend.vercel.app
    disk:
      name: atlas-data
      mountPath: /var/data
      sizeGB: 1
"@
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
