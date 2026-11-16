# Guitar Practice - small local web server for Windows. Nothing to install.
# Started by "Start Guitar Practice.bat". Serves this folder at http://localhost:8642
# so the app can be installed from Chrome or Edge and can use the microphone.
$ErrorActionPreference = 'Stop'
$Port = 8642
$Root = [System.IO.Path]::GetFullPath((Split-Path -Parent $MyInvocation.MyCommand.Path))
$RootPrefix = $Root.TrimEnd('\') + '\'
$Url = "http://localhost:$Port/index.html"
$Types = @{
  '.html' = 'text/html; charset=utf-8'
  '.js' = 'text/javascript; charset=utf-8'
  '.webmanifest' = 'application/manifest+json'
  '.json' = 'application/json'
  '.svg' = 'image/svg+xml'
  '.png' = 'image/png'
  '.txt' = 'text/plain; charset=utf-8'
  '.css' = 'text/css; charset=utf-8'
}

function Resolve-AppFile([string]$rawPath) {
  $p = $rawPath.Split('?')[0].Split('#')[0]
  $rel = [Uri]::UnescapeDataString($p).TrimStart('/')
  if ($rel -eq '') { $rel = 'index.html' }
  $rel = $rel.Replace('/', '\')
  $full = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($Root, $rel))
  if (-not $full.StartsWith($RootPrefix, [StringComparison]::OrdinalIgnoreCase)) { return $null }
  if (-not [System.IO.File]::Exists($full)) { return $null }
  return $full
}

function Get-ContentType([string]$file) {
  $e = [System.IO.Path]::GetExtension($file).ToLower()
  if ($Types.ContainsKey($e)) { return $Types[$e] }
  return 'application/octet-stream'
}

# Already running? Just open it.
try {
  $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
  if ($r.StatusCode -eq 200) {
    Write-Host 'Guitar Practice is already running.'
    Start-Process $Url
    exit 0
  }
} catch { }

# First choice: Windows' built-in HTTP server (works on localhost without admin rights).
$listener = $null
try {
  $listener = New-Object System.Net.HttpListener
  $listener.Prefixes.Add("http://localhost:$Port/")
  $listener.Start()
} catch {
  $listener = $null
}

# Fallback: a plain socket on 127.0.0.1.
$tcp = $null
if (-not $listener) {
  try {
    $tcp = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
    $tcp.Start()
  } catch {
    Write-Host "Could not start Guitar Practice on port ${Port}: $($_.Exception.Message)"
    Read-Host 'Press Enter to close'
    exit 1
  }
}

Write-Host "Guitar Practice is running at $Url"
Write-Host 'Leave this window open while you use or install the app. Close it to stop.'
Start-Process $Url

if ($listener) {
  while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $res = $ctx.Response
    try {
      $file = Resolve-AppFile $ctx.Request.RawUrl
      if ($file) {
        $bytes = [System.IO.File]::ReadAllBytes($file)
        $res.StatusCode = 200
        $res.ContentType = (Get-ContentType $file)
      } else {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes('Not found')
        $res.StatusCode = 404
        $res.ContentType = 'text/plain'
      }
      $res.AddHeader('Cache-Control', 'no-cache')
      $res.ContentLength64 = $bytes.Length
      if ($ctx.Request.HttpMethod -ne 'HEAD') { $res.OutputStream.Write($bytes, 0, $bytes.Length) }
    } catch {
    } finally {
      try { $res.Close() } catch { }
    }
  }
} else {
  while ($true) {
    $client = $tcp.AcceptTcpClient()
    try {
      $stream = $client.GetStream()
      $stream.ReadTimeout = 5000
      $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::ASCII, $false, 4096, $true)
      $line = $reader.ReadLine()
      while ($true) {
        $h = $reader.ReadLine()
        if ($h -eq $null -or $h -eq '') { break }
      }
      $method = 'GET'
      $file = $null
      if ($line) {
        $parts = $line.Split(' ')
        $method = $parts[0]
        if ($parts.Count -ge 2) { $file = Resolve-AppFile $parts[1] }
      }
      if ($file) {
        $bytes = [System.IO.File]::ReadAllBytes($file)
        $status = '200 OK'
        $type = Get-ContentType $file
      } else {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes('Not found')
        $status = '404 Not Found'
        $type = 'text/plain'
      }
      $head = "HTTP/1.1 $status`r`nContent-Type: $type`r`nContent-Length: $($bytes.Length)`r`nCache-Control: no-cache`r`nConnection: close`r`n`r`n"
      $hb = [System.Text.Encoding]::ASCII.GetBytes($head)
      $stream.Write($hb, 0, $hb.Length)
      if ($method -ne 'HEAD') { $stream.Write($bytes, 0, $bytes.Length) }
      $stream.Flush()
    } catch {
    } finally {
      $client.Close()
    }
  }
}
