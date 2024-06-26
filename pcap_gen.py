
# pcap_gen.py
# this code serves to generate synthetic pcap files readable by wireshark.
# the current implementation produces two pcap files, synthetic_pcap and 
# synthetic non_dga, which contain dgas taken from the 
# https://github.com/baderj/domain_generation_algorithms github page.
# 
# Author: Wesley Shen
#
# Last modified: April 19th, 2024

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

# performs main generation, with specified spikes and randomized ip addresses
# generates both benign and malicious traffic
def generate_synthetic_pcap(destination_domains, output_files, num_packets):
    packets_w_dga = []
    packets_wo_dga = []
    cur_time = 0
    # this points towards a cloud hosting server
    destination_domain = '54.39.23.28'

    # simulate infected device
    infected_device_ip = get_source_IP(0)
    infected_device_spikes = [200, 400, 600, 800, 1000]
    infected_device_DGA = random.randint(0, 6)
    second_infected_spike = 2000

    for i in range(num_packets):
        
        # gets a random source ip
        source_ip = get_source_IP()

        # particular infected device
        if i in infected_device_spikes:
            packet_seq = get_DGA_packet(infected_device_ip, destination_domain, infected_device_DGA)
            for packet in packet_seq:
                cur_time += DGA_timing_inc()
                packet.time = cur_time
            packets_w_dga.append(packet_seq)

        # DGA traffic
        elif i == second_infected_spike:
            packet_seq = get_DGA_packet(infected_device_ip, destination_domain)
            for packet in packet_seq:
                cur_time += DGA_timing_inc()
                packet.time = cur_time
            packets_w_dga.append(packet_seq)

        # non DGA traffic
        else:
            packet = get_non_DGA_packet(source_ip, destination_domain)
            cur_time += non_DGA_timing_inc()
            packet.time = cur_time
            packets_w_dga.append(packet)
            packets_wo_dga.append(packet)

    # writes the pcap to the outfile
    wrpcap(output_files[0], packets_w_dga)
    wrpcap(output_files[1], packets_wo_dga)

# gets random ip based on seed
def get_source_IP(seed=None):
    ip_array = ['192.168.1.100','10.0.0.2','172.16.0.1','169.254.0.1','198.51.100.1']
    if seed == None:
        return random.choice(ip_array)
    else:
        return ip_array[seed]

# returns single benign packet
def get_non_DGA_packet(source_ip, destination_domain):
    DGA_TAG = "NON"
    domain = ''.join(random.choice(destination_domains))
    packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))/Raw(load=DGA_TAG.encode())
    return packet

# determines timing between each of the non dga packets
def non_DGA_timing_inc():
    # these should have a range of a few milliseconds to a few seconds
    # want a bias towards the 0.5-1 range
    random_number = np.random.uniform(np.log(0.001), np.log(10))
    random_number = np.exp(random_number)

    return random_number

# returns sequence of packets that all have the same DGA on them
def get_DGA_packet(source_ip, destination_domain, seed=None):
    packet_seq = []
    DGA_TAG = "DGA"
    domain_list = pickDGA(seed)
    for d in domain_list:
        packet = Ether()/IP(src=source_ip, dst=destination_domain)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=d))/Raw(load=DGA_TAG.encode())
        packet_seq.append(packet)
    return packet_seq

# determines timing between each of the dga packets
def DGA_timing_inc():
    # these should have a range of a few microseconds to a few milliseconds
    # same bias as non dga, but for different range
    random_number = np.random.uniform(np.log(0.000001), np.log(0.01))
    random_number = np.exp(random_number)

    return random_number

# randomly selects a dga from the list
# 4/7 chance to choose non-dictionary
def pickDGA(seed = None, isdict = None):
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
    if seed == None:
        domain_list = dga_list[random.randint(0, len(dga_list)-1)]()
    else:
        domain_list = dga_list[seed]()
    return domain_list

# gets a list of the benign domains from the top 1000 list in cloudflare
# https://radar.cloudflare.com/domains
def get_domains():
    with open("benign_domains.csv", "r") as file:
        csv_reader = csv.reader(file)
        data_array = list(csv_reader)
    return data_array

if __name__ == "__main__":
    destination_domains = get_domains()
    output_files = ["synthetic_traffic.pcap", "synth_traffic_non_dga.pcap"]
    num_packets = 4500

    generate_synthetic_pcap(destination_domains, output_files, num_packets)
    for output in output_files:
        print(f"Synthetic PCAP file '{output}' generated successfully.")
