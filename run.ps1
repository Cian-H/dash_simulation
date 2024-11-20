$ErrorActionPreference = "Stop"

function Cleanup {
    $cachePath = Join-Path -Path "." -ChildPath "cache\live\*"
    if (Test-Path $cachePath) {
        Remove-Item -Path $cachePath -Recurse -Force
    }
}

try {
    $task1 = Start-Process -FilePath "python" -ArgumentList "-m panel serve ./dash_simulation/app.py --show" -NoNewWindow -PassThru
    $task2 = Start-Process -FilePath "./simulate_printer.nu" -NoNewWindow -PassThru

    $task1.WaitForExit()
    $task2.WaitForExit()
} finally {
    Cleanup
}
