$basePort = 8765

# Reuse an already running filoMacchine instance instead of launching a duplicate.
try {
    $state = Invoke-RestMethod -Uri "http://127.0.0.1:$basePort/api/state" -TimeoutSec 1
    if ($state.machines -and $state.works -and $state.services) {
        Write-Output "RUNNING:$basePort"
        exit 0
    }
} catch {
    # The default port may belong to another program or no program at all.
}

# Bind briefly to discover the first free localhost port.
for ($port = $basePort; $port -le 8800; $port++) {
    $listener = $null
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
        $listener.Start()
        $listener.Stop()
        Write-Output "FREE:$port"
        exit 0
    } catch {
        if ($listener) { $listener.Stop() }
    }
}

exit 1
