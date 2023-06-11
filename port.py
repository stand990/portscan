import socket
import concurrent.futures

def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set a timeout value for the connection attempt

    result = sock.connect_ex((ip, port))

    if result == 0:
        return ip, port

    sock.close()
    return None

def scan_ip(ip, port_list, output_file, progress_callback=None):
    open_ports = []
    total_ports = len(port_list)
    scanned_ports = 0

    for port in port_list:
        result = scan_port(ip, port)
        if result:
            open_ports.append(result)
            with open(output_file, 'a') as f:
                f.write(f"{result[0]}:{result[1]}\n")
                f.flush()  # Flush the file buffer to ensure immediate write
            print(f"Open port {result[1]} found on {result[0]}")

        scanned_ports += 1
        if progress_callback:
            progress_callback(scanned_ports, total_ports)

    return open_ports

def scan_open_ports(ip_list, port_list, output_file):
    open_ports = []
    total_ips = len(ip_list)
    scanned_ips = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        future_to_ip = {executor.submit(scan_ip, ip, port_list, output_file, progress_callback=progress_update): ip for ip in ip_list}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                open_ports.extend(future.result())
            except Exception as e:
                print(f"Error scanning {ip}: {str(e)}")

            scanned_ips += 1
            progress_update(scanned_ips, total_ips, prefix='Scanning IPs:', suffix='Complete', length=50)

    return open_ports

def progress_update(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

# Read IP addresses from file
ip_list_file = 'ip_list.txt'
with open(ip_list_file, 'r') as f:
    ip_list = f.read().splitlines()

# Read ports from file
port_range_file = 'port_range.txt'
with open(port_range_file, 'r') as f:
    port_list = [int(port) for port in f.read().splitlines()]

output_file = 'open_ports.txt'
with open(output_file, 'w') as f:
    pass  # Create an empty file to start with

open_ports = scan_open_ports(ip_list, port_list, output_file)
