#requires -Version 7.0
<#
Windows wrapper for the PRIVATE-only original-source uploader.

Create a PRIVATE repository with a README before use; install GitHub CLI,
run gh auth login, and keep the manifest-named 17 files in one source folder.

pwsh -File scripts/publish_solar_source_release.ps1 -SourceDirectory 'E:\Kerala2040\solar-originals'

This script never uploads to public kerala2040. Publisher terms still apply.
#>
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string] $SourceDirectory,
 [string] $ArchiveRepo = "abhijith-sivaprasadan/kerala2040-source-archive"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "publish_solar_source_release.py"
python $script --source-dir $SourceDirectory --archive-repo $ArchiveRepo
if ($LASTEXITCODE -ne 0) {
 throw "Private source archive upload failed. The original source files remain local."
}
