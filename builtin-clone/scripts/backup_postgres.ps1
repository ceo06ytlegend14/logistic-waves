[CmdletBinding()]
param(
    [string]$BackupDirectory = "$PSScriptRoot\..\backups",
    [ValidateRange(1, 3650)]
    [int]$RetentionDays = 30
)

$ErrorActionPreference = 'Stop'
$databaseUrl = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { $env:POSTGRES_URL }
if (-not $databaseUrl) {
    throw 'DATABASE_URL or POSTGRES_URL must be set. The database URL is never written to output.'
}
if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw 'pg_dump was not found. Install PostgreSQL client tools before scheduling backups.'
}

New-Item -ItemType Directory -Force -Path $BackupDirectory | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$target = Join-Path $BackupDirectory "logistic-waves-$stamp.dump"

& pg_dump --format=custom --no-owner --file $target $databaseUrl
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $target)) {
    throw 'pg_dump failed; the backup was not accepted.'
}

# Custom-format dumps can be integrity-listed without restoring production data.
& pg_restore --list $target | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item -LiteralPath $target -Force
    throw 'Backup verification failed; the unusable dump was removed.'
}

$cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -LiteralPath $BackupDirectory -Filter 'logistic-waves-*.dump' -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force

Write-Output "Verified PostgreSQL backup created: $target"
