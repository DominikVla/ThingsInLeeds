param(
    [string]$SourceDatabase = "things_in_leeds",
    [string]$ReadOnlyDatabase = "things_in_leeds_read_only",
    [string]$Username = "root",
    [switch]$DropExisting
)

$ErrorActionPreference = "Stop"

$commands = @("mysqldump", "mysql")
foreach ($command in $commands) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "'$command' was not found. Install MySQL client tools and add them to PATH."
    }
}

if ($DropExisting) {
    & mysql "-u$Username" "-e" "DROP DATABASE IF EXISTS `$ReadOnlyDatabase; CREATE DATABASE `$ReadOnlyDatabase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
} else {
    & mysql "-u$Username" "-e" "CREATE DATABASE IF NOT EXISTS `$ReadOnlyDatabase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
}

$tempDump = Join-Path ([System.IO.Path]::GetTempPath()) "things-in-leeds-readonly-$([guid]::NewGuid()).sql"
try {
    & mysqldump "-u$Username" --single-transaction --routines --triggers --events --no-tablespaces $SourceDatabase | Set-Content -Encoding utf8 $tempDump
    Get-Content -Raw $tempDump | & mysql "-u$Username" $ReadOnlyDatabase
} finally {
    Remove-Item $tempDump -ErrorAction SilentlyContinue
}

Write-Host "Created/updated read-only copy database '$ReadOnlyDatabase' from '$SourceDatabase'."
