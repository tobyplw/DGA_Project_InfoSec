import argparse
from scapy.all import rdpcap, DNSQR, IP
import pandas as pd
import matplotlib.pyplot as plt
from predict import predictor
from collections import defaultdict
import matplotlib.dates as mdates

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
    results = {'source_ip': [], 'domain': [], 'isDGA': [], 'timestamp': []}
    for source_ip, domain, timestamp in domain_info:
        isDGA_combined = False
        if pred.predict_isDga(domain):
            isDGA_combined = True
        else:
            if pred.predict_isDictDga(domain):
                isDGA_combined = True
        results['source_ip'].append(source_ip)
        results['domain'].append(domain)
        results['isDGA'].append(isDGA_combined)
        results['timestamp'].append(timestamp)
    return results



def generate_frequency_graph(data_frame):
    for source_ip, df_group in data_frame.groupby('source_ip'):
        df_group['timestamp'] = pd.to_datetime(df_group['timestamp'].astype(float), unit='s')
        start_time = df_group['timestamp'].min()
        end_time = df_group['timestamp'].max()
        ts_resampled = df_group.set_index('timestamp').resample('10S').size()
        moving_avg = ts_resampled.rolling(window=6, min_periods=1).mean()
        plt.figure(figsize=(15, 7))
        plt.plot(moving_avg.index, moving_avg.values, marker='o', linestyle='-')
        plt.title(f"DGA Query Frequency Over Time for IP: {source_ip}")
        plt.xlabel("Time")
        plt.ylabel("Frequency (DGA Hits per 10 seconds)")
        plt.xlim(start_time, end_time)
        myFmt = mdates.DateFormatter('%m-%d %H:%M:%S')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        plt.gcf().autofmt_xdate()
        plt.show()

def generate_report(results, report_path):
    df = pd.DataFrame(results)
    df.to_csv(report_path, index=False)
    print(f"Report generated: {report_path}")

def create_source_ip_profiles(df):
    profiles = defaultdict(lambda: {'total_queries': 0, 'dga_queries': 0})
    for index, row in df.iterrows():
        profiles[row['source_ip']]['total_queries'] += 1
        if row['isDGA']:
            profiles[row['source_ip']]['dga_queries'] += 1
    for ip, profile in profiles.items():
        total = profile['total_queries']
        dga = profile['dga_queries']
        likelihood = dga / total if total > 0 else 0
        profile['likelihood_score'] = likelihood
    return profiles

def save_profiles_to_csv(profiles, filename):
    profiles_df = pd.DataFrame.from_dict(profiles, orient='index').reset_index()
    profiles_df.rename(columns={'index': 'source_ip'}, inplace=True)
    profiles_df.to_csv(filename, index=False)
    print(f"Profiles saved to {filename}")


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
    df = pd.DataFrame(results)

    if args.plot:
        print("Generating frequency plots...")
        generate_frequency_graph(df)

    print("Generating report...")
    generate_report(results, args.report)

    print("Creating source IP profiles...")
    profiles = create_source_ip_profiles(df)
    save_profiles_to_csv(profiles, 'source_ip_profiles.csv')
