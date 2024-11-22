$ErrorActionPreference = "Stop"

function Cleanup {
    $cachePath = Join-Path -Path "." -ChildPath "cache\live\*"
    if (Test-Path $cachePath) {
        Remove-Item -Path $cachePath -Recurse -Force
    }
    $layersPath = Join-Path -Path "." -ChildPath "layers\*"
    if (Test-Path $layersPath) {
        Remove-Item -Path $layersPath -Recurse -Force
    }
}

try {
    $task1 = Start-Process -FilePath "python" -ArgumentList "-m dash_simulation" -NoNewWindow -PassThru
    $task2 = Start-Process -FilePath "./simulate_printer.nu" -NoNewWindow -PassThru

    $task1.WaitForExit()
    $task2.WaitForExit()
} finally {
    Cleanup
}
