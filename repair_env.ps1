# Force TLS 1.2 for modern web requests
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "========================================"
Write-Host " UNIVERSAL HARVESTER - ENV REPAIR"
Write-Host "========================================"

# --- Node.js Fix -------------------------------------------------------------

Write-Host "`n[+] Checking Node.js version..."
$nodeVersion = node -v 2>$null

if ($nodeVersion) {
    Write-Host "    [OK] Node.js version detected: $nodeVersion"
    if ($nodeVersion -notmatch "^v20") {
        Write-Host "    [X] Unsupported Node version. Installing Node.js 20 LTS..."

        $url = "https://nodejs.org/dist/latest-v20.x/node-v20.15.0-x64.msi"
        $installer = "$env:TEMP\node20.msi"

        Write-Host "    [>] Downloading Node.js 20 LTS..."
        Invoke-WebRequest -Uri $url -OutFile $installer

        Write-Host "    [>] Installing Node.js 20 LTS..."
        Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installer`" /qn"
    }
} else {
    Write-Host "    [X] Node.js not found. Installing Node.js 20 LTS..."

    $url = "https://nodejs.org/dist/latest-v20.x/node-v20.15.0-x64.msi"
    $installer = "$env:TEMP\node20.msi"

    Write-Host "    [>] Downloading Node.js 20 LTS..."
    Invoke-WebRequest -Uri $url -OutFile $installer

    Write-Host "    [>] Installing Node.js 20 LTS..."
    Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installer`" /qn"
}

# --- DNS & Network Fix -------------------------------------------------------

Write-Host "`n[+] Flushing DNS..."
ipconfig /flushdns | Out-Null

Write-Host "[+] Detecting active network adapter..."
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1

if ($adapter) {
    Write-Host "    [OK] Active adapter: $($adapter.Name)"
    Write-Host "    [>] Disabling IPv6 to prevent DNS hijacking..."
    Disable-NetAdapterBinding -Name $adapter.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue

    Write-Host "    [>] Setting DNS to Cloudflare (1.1.1.1, 1.0.0.1)..."
    Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ServerAddresses ("1.1.1.1","1.0.0.1")
}

# --- HuggingFace Connectivity Test ------------------------------------------

Write-Host "`n[+] Testing Hugging Face connectivity..."
try {
    Invoke-WebRequest -Uri "https://api-inference.huggingface.co" -TimeoutSec 10 | Out-Null
    Write-Host "    [OK] Hugging Face reachable."
} catch {
    Write-Host "    [X] Hugging Face unreachable: $($_.Exception.Message)"
}

# --- Playwright Test ---------------------------------------------------------

Write-Host "`n[+] Testing Playwright browser launch..."
try {
    python -c "from playwright.sync_api import sync_playwright; \
with sync_playwright() as p: \
    b = p.chromium.launch(headless=True); \
    page = b.new_page(); \
    page.goto('https://example.com', timeout=15000); \
    b.close()"
    Write-Host "    [OK] Playwright working."
} catch {
    Write-Host "    [X] Playwright test failed: $($_.Exception.Message)"
}

Write-Host "`n========================================"
Write-Host " ENVIRONMENT REPAIR COMPLETE"
Write-Host "========================================"
