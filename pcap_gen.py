import random
import socket
from datetime import datetime, timedelta
from scapy.all import IP, UDP, DNS, DNSQR, Ether, Raw, wrpcap
import csv
import time
import base64
from ctypes import c_uint 
from itertools import product
import numpy as np
from dgas import *

def generate_synthetic_pcap(destination_domains, output_file, num_packets):
    packets_w_dga = []
    packets_wo_dga = []
    cur_time = 0
    # this points towards a cloud hosting server
    destination_domain = '54.39.23.28'

    # simulate infected device
    infected_device_ip = get_source_IP(0)
    infected_device_spikes = [200, 400, 600, 800, 1000]
    infected_device_DGA = random.randint(0, 6)

    for i in range(num_packets):
        
        # gets a random source ip
        source_ip = get_source_IP(99)

        # partiuclar infected device
        if i in infected_device_spikes:
            packet_seq = get_DGA_packet(infected_device_ip, destination_domain, infected_device_DGA)
            for packet in packet_seq:
                cur_time += DGA_timing_inc()
                packet.time = cur_time
            packets_w_dga.append(packet_seq)

        # DGA traffic
        elif i == 2000:
            packet_seq = get_DGA_packet(source_ip, destination_domain, 99)
            for packet in packet_seq:
                cur_time += DGA_timing_inc()
                packet.time = cur_time
            packets_w_dga.append(packet_seq)
        
        # non DGA traffic spike
        # 10% chance of triggering
        elif random.randint(0,19) == 0:
            packet_spike_length = random.randint(10,20)
            packet_seq = []
            for j in range(packet_spike_length):
                packet = get_non_DGA_packet(source_ip, destination_domain)
                cur_time += DGA_timing_inc()
                packet.time = cur_time
                packets_w_dga.append(packet)
                packets_wo_dga.append(packet)

        # non DGA traffic
        else:
            packet = get_non_DGA_packet(source_ip, destination_domain)
            cur_time += non_DGA_timing_inc()
            packet.time = cur_time
            packets_w_dga.append(packet)
            packets_wo_dga.append(packet)

    # writes the pcap to the outfile
    wrpcap(output_file, packets_w_dga)
    wrpcap("synth_traffic_non_dga.pcap", packets_wo_dga)

def get_source_IP(seed):
    ip_array = ['192.168.1.100','10.0.0.2','172.16.0.1','169.254.0.1','198.51.100.1']
    if seed == 99:
        return random.choice(ip_array)
    else:
        return ip_array[seed]

# returns single packet
def get_non_DGA_packet(source_ip, destination_domain):
    DGA_TAG = "NON"
    domain = ''.join(random.choice(destination_domains))
    packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))/Raw(load=DGA_TAG.encode())
    return packet

def non_DGA_timing_inc():
    # these should have a range of a few milliseconds to a few seconds
    # want a bias towards the 0.5-1 range
    random_number = np.random.uniform(np.log(0.001), np.log(10))
    random_number = np.exp(random_number)

    return random_number

# returns sequence of packets
def get_DGA_packet(source_ip, destination_domain, seed):
    packet_seq = []
    DGA_TAG = "DGA"
    domain_list = pickDGA(seed)
    for d in domain_list:
        packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=d))/Raw(load=DGA_TAG.encode())
        packet_seq.append(packet)
    return packet_seq

def DGA_timing_inc():
    # these should have a range of a few microseconds to a few milliseconds
    # same bias
    random_number = np.random.uniform(np.log(0.000001), np.log(0.01))
    random_number = np.exp(random_number)

    return random_number

def pickDGA(seed):
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
    if seed == 99:
        domain_list = dga_list[random.randint(0, len(dga_list)-1)]()
    else:
        domain_list = dga_list[seed]()
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
    num_packets = 4500

    generate_synthetic_pcap(destination_domains, output_file, num_packets)
    print(f"Synthetic PCAP file '{output_file}' generated successfully.")
