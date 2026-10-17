param(
    [Parameter(Mandatory=$true)][string]$Narration,
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$Voice = "Microsoft Zira Desktop",
    [int]$Rate = 1
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.SelectVoice($Voice)
$speaker.Rate = $Rate
$speaker.Volume = 100
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$items = Get-Content -LiteralPath $Narration -Raw -Encoding UTF8 | ConvertFrom-Json
for ($i = 0; $i -lt $items.Count; $i++) {
    $target = Join-Path $Output ('speech-{0:d2}.wav' -f $i)
    $speaker.SetOutputToWaveFile($target)
    $speaker.Speak($items[$i].spoken)
    $speaker.SetOutputToNull()
}
$speaker.Dispose()
