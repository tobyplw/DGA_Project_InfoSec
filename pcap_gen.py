import random
import socket
from datetime import datetime, timedelta
from scapy.all import IP, UDP, DNS, DNSQR, Ether, wrpcap
import csv
import time
import base64
from ctypes import c_uint 
from itertools import product
import numpy as np
from dgas import *


def generate_synthetic_pcap(destination_domains, output_file, num_packets=100):
    packets = []
    cur_time = 0
    # this points towards a cloud hosting server
    destination_domain = '54.39.23.28'

    for i in range(num_packets):
        source_ip = get_source_IP()

        # non DGA traffic
        if i != 33:
            packet = get_non_DGA_packet(source_ip, destination_domain)
            cur_time += non_DGA_timing_inc()
            packet.time = cur_time
            packets.append(packet)
        
        # DGA traffic
        else:
            packet_seq = get_DGA_packet(source_ip, destination_domain)
            for packet in packet_seq:
                cur_time += DGA_timing_inc()
                packet.time = cur_time
            packets.append(packet_seq)

    # writes the pcap to the outfile
    wrpcap(output_file, packets)

def get_source_IP():
    
    return random.choice(['192.168.1.100','10.0.0.2','172.16.0.1','169.254.0.1','198.51.100.1'])

# returns single packet
def get_non_DGA_packet(source_ip, destination_domain):
    domain = ''.join(random.choice(destination_domains))
    packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
    return packet

def non_DGA_timing_inc():
    # these should have a range of a few milliseconds to a few seconds
    # want a bias towards the 0.5-1 range
    random_number = np.random.uniform(np.log(0.001), np.log(10))
    random_number = np.exp(random_number)

    return random_number

# returns sequence of packets
def get_DGA_packet(source_ip, destination_domain):
    packet_seq = []
    domain_list = pickDGA(destination_domain)
    for d in domain_list:
        packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=d))
        packet_seq.append(packet)
    return packet_seq

def DGA_timing_inc():
    # these should have a range of a few microseconds to a few milliseconds
    # same bias
    random_number = np.random.uniform(np.log(0.000001), np.log(0.01))
    random_number = np.exp(random_number)

    return random_number

def pickDGA(destination_domain):
    domain_list = []
    dga_list = {
        # non dictionary DGA
        0: bazarDGA,
        1: cryptolockerDGA,
        2: dmsniffDGA,
        3: sisronDGA,
        # dictionary dga
        4: suppoboxDGA,
        5: goziDGA,
        6: banjoriDGA
    }
    for i in range(len(dga_list)):
        domain_list = dga_list[i]()
    domain_list = dga_list[random.randint(0, len(dga_list)-1)]()
    domain_list = dga_list[5]()
    return domain_list

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

    generate_synthetic_pcap(destination_domains, output_file, num_packets)
    print(f"Synthetic PCAP file '{output_file}' generated successfully.")


    # method w/ five different IPs to emulate
    # change