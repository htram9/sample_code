$InstanceName='MSSQLSERVER'
$workingNamespace="root\Microsoft\SqlServer\ComputerManagement16"     # SQL Server 2022 specific!

Get-Service -Name $InstanceName   # Verify installation

# Enable listening on port 1433
Write-Host "Attempting to enable port 1433..."

$tcp = Get-WmiObject -Namespace $workingNamespace -Class ServerNetworkProtocol -Filter "InstanceName='$InstanceName' AND ProtocolName='Tcp'"
$tcp.SetEnable()
$tcpProps = Get-WmiObject -Namespace $workingNamespace -Class ServerNetworkProtocolProperty -Filter "InstanceName='$InstanceName' AND ProtocolName='Tcp'"
$tcpPort = $tcpProps | Where-Object { $_.PropertyName -eq "TcpPort" -and $_.IPAddressName -eq "IPAll" }
$tcpPort.SetStringValue("1433")
$dynamicPort = $tcpProps | Where-Object { $_.PropertyName -eq "TcpDynamicPorts" -and $_.IPAddressName -eq "IPAll" }
$dynamicPort.SetStringValue("")

# Add firewall rule to allow inbound connections to 1433
Write-Host "Attempting to add firewall rule to allow SQL Server remote access..."
New-NetFirewallRule -DisplayName "SQL Server Remote Access" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow -ErrorAction SilentlyContinue

Write-Host "Done enabling port for SQL Server..."
