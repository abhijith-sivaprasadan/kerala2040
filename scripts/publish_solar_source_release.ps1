#requires -Version 7.0
<#
Archive this verified batch of user-provided originals as GitHub Release assets.
GitHub's normal Git history is deliberately not used for 300+ MB ZIPs.
Only run after reviewing public redistribution rights for EVERY asset,
especially the mixed Solar.zip bundle and third-party PDFs.
The release is created as draft and published only with -Publish.
Example (files all in E:\Kerala2040\SolarSources):
  pwsh -File scripts/publish_solar_source_release.ps1 -SourceDirectory 'E:\Kerala2040\SolarSources' -IHaveCheckedPublicRedistributionRights -Publish
#>
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string] $SourceDirectory,
 [switch] $IHaveCheckedPublicRedistributionRights,
 [switch] $Publish,
 [string] $Repo = "abhijith-sivaprasadan/kerala2040"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (-not $IHaveCheckedPublicRedistributionRights) {
 throw "Review the public-release rights of Solar.zip and every PDF first; then explicitly pass -IHaveCheckedPublicRedistributionRights."
}
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$manifest = Get-Content -Raw (Join-Path $root "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json") | ConvertFrom-Json
$source = (Resolve-Path $SourceDirectory).Path
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "Install GitHub CLI (gh) first." }
gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) { throw "gh auth status failed. Authenticate with gh auth login." }
$verified = @()
foreach ($item in $manifest.assets) {
 $file = Join-Path $source $item.name
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing original: $file" }
 $info = Get-Item -LiteralPath $file
 if ($info.Length -ne $item.bytes) { throw "Size mismatch: $file" }
 $hash = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
 if ($hash -ne $item.sha256) { throw "SHA256 mismatch: $file" }
 $verified += $file
 Write-Host "SHA256 verified: $($item.name)"
}
$tag = $manifest.release_tag
$release = & gh release view $tag --repo $Repo --json isDraft,assets 2>$null
if ($LASTEXITCODE -ne 0) {
 & gh release create $tag --repo $Repo --target main --title "Kerala2040: original solar source batch 2026-09-21" --notes "Original, checksum-verified source archives. Exact publisher links, individual SHA256s, temporal limitations and attribution: data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json. Data are not automatically admitted to the model." --draft
 if ($LASTEXITCODE -ne 0) { throw "Could not create draft release." }
} else {
 $existing = $release | ConvertFrom-Json
 if (-not $existing.isDraft) { throw "Release already public. Refusing to overwrite existing assets." }
}
foreach ($file in $verified) {
 & gh release upload $tag $file --repo $Repo --clobber
 if ($LASTEXITCODE -ne 0) { throw "Release upload failed for $file; draft kept for retry." }
}
$info = (& gh release view $tag --repo $Repo --json isDraft,assets) | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Could not verify GitHub Release." }
foreach ($item in $manifest.assets) {
 $matches = @($info.assets | Where-Object { $_.name -eq $item.name })
 if ($matches.Count -ne 1 -or $matches[0].size -ne $item.bytes) { throw "Release missing or different-size asset: $($item.name)" }
}
Write-Host "All eight release assets present with matching sizes. Tag: $tag"
if ($Publish) {
 & gh release edit $tag --repo $Repo --draft=false
 if ($LASTEXITCODE -ne 0) { throw "Assets uploaded but publishing failed: draft release retained." }
 Write-Host "Published public source archive: https://github.com/$Repo/releases/tag/$tag"
} else {
 Write-Host "Release remains DRAFT. Inspect redistribution terms and use: gh release edit $tag --repo $Repo --draft=false"
}
