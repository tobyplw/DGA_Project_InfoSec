import argparse
from scapy.all import rdpcap, DNSQR, IP
import pandas as pd
import matplotlib.pyplot as plt
from predict import predictor

def extract_domain_info(pcap_path):
    packets = rdpcap(pcap_path)
    domain_info = []
    for packet in packets:
        if packet.haslayer(DNSQR) and packet.haslayer(IP):
            timestamp = packet.time
            source_ip = packet[IP].src
            domain = packet[DNSQR].qname.decode("utf-8").rstrip('.')
            domain_info.append((source_ip, domain, timestamp))
    return domain_info

def analyze_domains(domain_info, pred):
    results = {'source_ip': [], 'domain': [], 'isDGA': [], 'isDictDGA': [], 'timestamp': []}
    for source_ip, domain, timestamp in domain_info:
        isDGA = pred.predict_isDga(domain)
        isDictDGA = pred.predict_isDictDga(domain)
        results['source_ip'].append(source_ip)
        results['domain'].append(domain)
        results['isDGA'].append(isDGA)
        results['isDictDGA'].append(isDictDGA)
        results['timestamp'].append(timestamp)
    return results

def generate_frequency_graph(data_frame):
    for source_ip, df_group in data_frame.groupby('source_ip'):
        df_group['timestamp'] = pd.to_datetime(df_group['timestamp'].astype(float), unit='s')
        ts_resampled = df_group.set_index('timestamp').resample('H').size()

        plt.figure(figsize=(10, 6))
        plt.plot(ts_resampled.index, ts_resampled.values, marker='o', linestyle='-')
        plt.title(f"Domain Query Frequency Over Time for IP: {source_ip}")
        plt.xlabel("Time")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def generate_report(results, report_path):
    df = pd.DataFrame(results)
    df.to_csv(report_path, index=False)
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a PCAP file for DGA domains and plot query frequencies.")
    parser.add_argument("pcap_path", help="Path to the PCAP file")
    parser.add_argument("--report", default="dga_report.csv", help="Path to the output report CSV file")
    parser.add_argument("--plot", action="store_true", help="Generate and display frequency plots for each source IP")

    args = parser.parse_args()

    print("Extracting domains and source IPs from PCAP...")
    domain_info = extract_domain_info(args.pcap_path)

    print("Initializing models...")
    pred = predictor()

    print("Analyzing domains...")
    results = analyze_domains(domain_info, pred)

    if args.plot:
        print("Generating frequency plots...")
        df = pd.DataFrame(results)
        generate_frequency_graph(df)

    print("Generating report...")
    generate_report(results, args.report)