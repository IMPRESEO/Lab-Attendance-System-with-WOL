`"""
Network Wake on LAN functionality for attendance system
"""
import socket
import subprocess
import platform
import time

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def wake_on_lan(mac_address, broadcast_ip="255.255.255.255", port=9):
    """
    Send Wake-on-LAN magic packet to wake up a device
    """
    try:
        # Create the Wake-on-LAN magic packet
        mac_bytes = bytes.fromhex(mac_address.replace(":", "").replace("-", ""))
        
        # Build the packet
        packet = b'\xff' * 6 + mac_bytes * 16
        
        # Send the packet
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, (broadcast_ip, port))
            
        return True, "Wake-on-LAN packet sent successfully"
        
    except Exception as e:
        return False, f"Error sending Wake-on-LAN packet: {str(e)}"

def wake_on_lan_with_ip(mac_address, target_ip, port=9):
    """
    Send Wake-on-LAN magic packet to a specific IP address
    """
    try:
        # Create the Wake-on-LAN magic packet
        mac_bytes = bytes.fromhex(mac_address.replace(":", "").replace("-", ""))
        
        # Build the packet
        packet = b'\xff' * 6 + mac_bytes * 16
        
        # Send the packet to specific IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(packet, (target_ip, port))
            
        return True, f"Wake-on-LAN packet sent to {target_ip}"
        
    except Exception as e:
        return False, f"Error sending Wake-on-LAN packet: {str(e)}"

def get_network_interfaces():
    """
    Get available network interfaces and their IP addresses
    """
    try:
        if platform.system() == "Windows":
            # Windows command to get network interfaces
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            interfaces = []
            
            for line in result.stdout.split('\n'):
                if 'Ethernet adapter' in line or 'Wireless LAN adapter' in line:
                    interface = {}
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        interface['name'] = parts[0].strip()
                        for part in parts[1:]:
                            if 'IPv4 Address' in part:
                                interface['ip'] = part.split(':')[1].strip()
                            elif 'Physical Address' in part:
                                interface['mac'] = part.split(':')[1].strip()
                    if interface:
                        interfaces.append(interface)
            
            return interfaces
        else:
            # Linux/Mac command to get network interfaces
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            interfaces = []
            
            current_interface = {}
            for line in result.stdout.split('\n'):
                if line.strip():
                    if line.startswith(' '):
                        if current_interface:
                            interfaces.append(current_interface)
                            current_interface = {}
                        parts = line.strip().split()
                        for part in parts:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                current_interface[key.strip()] = value.strip()
                    else:
                        current_interface['raw'] = line.strip()
            
            if current_interface:
                interfaces.append(current_interface)
            
            return interfaces
            
    except Exception as e:
        return []

def scan_network_for_devices():
    """
    Scan the network to find devices that might be wakeable
    """
    devices = []
    
    try:
        local_ip = get_local_ip()
        network = local_ip.rsplit('.', 1)[0] + '.0'
        
        # Scan common IP range
        for i in range(1, 255):
            ip = f"{network}.{i}"
            
            # Try to ping the IP
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                          capture_output=True, text=True)
                else:
                    result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Try to get MAC address using ARP
                    try:
                        if platform.system() == "Windows":
                            arp_result = subprocess.run(['arp', '-a', ip], 
                                                      capture_output=True, text=True)
                        else:
                            arp_result = subprocess.run(['arp', '-n', ip], 
                                                      capture_output=True, text=True)
                        
                        mac_address = "Unknown"
                        for line in arp_result.stdout.split('\n'):
                            if ip in line:
                                parts = line.split()
                                for part in parts:
                                    if part.strip() and len(part.strip()) == 17:
                                        mac_address = part.strip()
                        
                        devices.append({
                            'ip': ip,
                            'mac': mac_address,
                            'status': 'online'
                        })
                        
            except Exception:
                pass
                
    except Exception as e:
        print(f"Network scan error: {str(e)}")
    
    return devices

def create_wake_up_script():
    """
    Create a PowerShell script for Windows Wake-on-LAN
    """
    script_content = '''
# Wake-on-LAN PowerShell Script
param(
    [Parameter(Mandatory=$true)]
    [string]$MacAddress
)

# Convert MAC address format
$MacAddress = $MacAddress -replace ":", "").replace "-", "").ToUpper()

# Validate MAC address
if ($MacAddress.Length -ne 12) {
    Write-Error "Invalid MAC address format. Use format: XX:XX:XX:XX:XX"
    exit 1
}

# Create Wake-on-LAN magic packet
$MacBytes = $MacAddress -split '([A-F0-9]{2})' | ForEach-Object { 
    [byte[]]$Bytes = [byte]::Parse($_, 'Hex')
}

$Packet = [byte[]](0xFF * 6) + $MacBytes * 16)

# Send the packet
$UdpClient = New-Object System.Net.Sockets.UdpClient
$UdpClient.EnableBroadcast = $true
$UdpClient.Connect(([System.Net.IPAddress]::Broadcast, 9), $null)

try {
    $UdpClient.Send($Packet, 0, $Packet.Length)
    Write-Host "Wake-on-LAN packet sent to $MacAddress" -ForegroundColor Green
} catch {
    Write-Error "Failed to send Wake-on-LAN packet: $_" -ForegroundColor Red
} finally {
    $UdpClient.Close()
    Write-Host "Wake-on-LAN operation completed"
}
'''
    
    with open('wake_on_lan.ps1', 'w') as f:
        f.write(script_content)
    
    return 'wake_on_lan.ps1'

if __name__ == "__main__":
    # Test functions
    print("Network Wake-on-LAN Tools")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"Local IP: {local_ip}")
    
    # Get network interfaces
    interfaces = get_network_interfaces()
    print("\nNetwork Interfaces:")
    for interface in interfaces:
        print(f"  {interface.get('name', 'Unknown')}: {interface.get('ip', 'Unknown')}")
        if 'mac' in interface:
            print(f"    MAC: {interface['mac']}")
    
    # Create PowerShell script
    script_path = create_wake_up_script()
    print(f"\nPowerShell script created: {script_path}")
    
    # Example usage
    print("\nExample Usage:")
    print("1. Python: wake_on_lan.py 'AA:BB:CC:DD:EE:FF'")
    print("2. PowerShell: .\\wake_on_lan.ps1 -MacAddress 'AA:BB:CC:DD:EE:FF'")
    print("\n3. Broadcast: wake_on_lan.py 'AA:BB:CC:DD:EE:FF' '255.255.255.255'")
    
    # Network scan
    print("\nScanning network for devices...")
    devices = scan_network_for_devices()
    
    if devices:
        print("\nDevices found:")
        for device in devices:
            print(f"  IP: {device['ip']}, MAC: {device['mac']}, Status: {device['status']}")
    else:
        print("No devices found on network")
