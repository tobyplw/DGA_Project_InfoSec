import random
import socket
from scapy.all import IP, UDP, DNS, DNSQR, Ether, wrpcap
import csv


def generate_synthetic_pcap(source_ip, destination_domains, output_file, num_packets=100):
    packets = []

    for i in range(num_packets):
        # non DGA traffic
        if i != 33:
            destination_domain = ''.join(random.choice(destination_domains))
            try:
                packet = Ether()/IP(src=source_ip, dst=socket.gethostbyname(destination_domain))/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=destination_domain))
                packets.append(packet)
            except:
                print(destination_domain + " is invalid")
        
        # DGA traffic
        else:
            for j in range(30): 
                domain = DGA(j, j+1, j+2)
                try:
                    packet = Ether()/IP(src=source_ip, dst=socket.gethostbyname(domain))/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                except:
                    packet = Ether()/IP(src=source_ip, dst='8.8.8.8')/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                packets.append(packet)

    wrpcap(output_file, packets)

def DGA(year, month, day):  
    domain = ""

    for _ in range(16):
        year = ((year ^ 8 * year) >> 11) ^ ((year & 0xFFFFFFF0) << 17)
        month = ((month ^ 4 * month) >> 25) ^ 16 * (month & 0xFFFFFFF8)
        day = ((day ^ (day << 13)) >> 19) ^ ((day & 0xFFFFFFFE) << 12)
        domain += chr(((year ^ month ^ day) % 25) + 97)

    return domain + ".com"


def get_domains():
    with open("benign_domains.csv", "r") as file:
        csv_reader = csv.reader(file)
        data_array = list(csv_reader)
    return data_array


if __name__ == "__main__":
    source_ip = "192.168.1.100"  # Replace with the source IoT device IP
    destination_domains = get_domains()
    output_file = "synthetic_traffic.pcap"
    num_packets = 100

    generate_synthetic_pcap(source_ip, destination_domains, output_file, num_packets)
    print(f"Synthetic PCAP file '{output_file}' generated successfully.")