import argparse
from scapy.all import rdpcap, DNSQR, IP, Raw
import pandas as pd
import matplotlib.pyplot as plt
from predict import predictor
from collections import defaultdict
import matplotlib.dates as mdates
import binascii

#Extract domain info from pcaps
def extract_domain_info(pcap_path):
    packets = rdpcap(pcap_path) #read packets
    domain_info = []
    for packet in packets:
        if packet.haslayer(DNSQR) and packet.haslayer(IP):
            timestamp = packet.time
            source_ip = packet[IP].src
            domain = packet[DNSQR].qname.decode("utf-8").rstrip('.')
            extraneous_data = binascii.hexlify(packet[Raw].load).decode('utf-8').upper() if packet.haslayer(Raw) else ""
            domain_info.append((source_ip, domain, timestamp, extraneous_data))
    return domain_info


#Analyze domains using the model
def analyze_domains(domain_info, pred, use_expected):
    results = {'source_ip': [], 'domain': [], 'isDGA': [], 'timestamp': []}
    for source_ip, domain, timestamp, extraneous_data in domain_info:
        if use_expected:
            isDGA_combined = False if "4E4F4E" in extraneous_data else True #check for extraneous data(--expected flag)
        else:
            isDGA_combined = pred.predict_isDga(domain)
            if not isDGA_combined:
                isDGA_combined = pred.predict_isDictDga(domain)
        results['source_ip'].append(source_ip)
        results['domain'].append(domain)
        results['isDGA'].append(isDGA_combined)
        results['timestamp'].append(timestamp)
    return results


#Generate frequency graphs for each profile
def generate_frequency_graph(data_frame):
    for source_ip, df_group in data_frame.groupby('source_ip'):
        df_group['isDGA'] = df_group['isDGA'].astype(int)
        df_group['timestamp'] = pd.to_datetime(df_group['timestamp'].astype(float), unit='s')
        ts_resampled = df_group.set_index('timestamp').resample('10S')['isDGA'].sum()
        moving_avg = ts_resampled.rolling(window=6, min_periods=1).mean()
        
        plt.figure(figsize=(15, 7))
        plt.plot(moving_avg.index, moving_avg.values, marker='o', linestyle='-')
        plt.title(f"DGA Query Frequency Over Time for IP: {source_ip}")
        plt.xlabel("Time")
        plt.ylabel("Frequency (DGA Hits per 10 seconds)")
        plt.xlim(df_group['timestamp'].min(), df_group['timestamp'].max())
        plt.ylim(bottom=0) 
        myFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        plt.gcf().autofmt_xdate()
        plt.show()


#Generate the csv report(--report flag)
def generate_report(results, report_path):
    df = pd.DataFrame(results)
    df.to_csv(report_path, index=False)
    print(f"Report generated: {report_path}")

#creates source profiles
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

#Save each unique profile to another csv
def save_profiles_to_csv(profiles, filename):
    profiles_df = pd.DataFrame.from_dict(profiles, orient='index').reset_index()
    profiles_df.rename(columns={'index': 'source_ip'}, inplace=True)
    profiles_df.to_csv(filename, index=False)
    print(f"Profiles saved to {filename}")

#Provides an 'alert' based on the given threshold
def alert_on_possible_infection(profiles, threshold=0.5):
    for ip, profile in profiles.items():
        if profile['likelihood_score'] > threshold:
            print(f"ALERT: Potential DGA malware infection detected on IP: {ip}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a PCAP file for DGA domains and plot query frequencies.")
    parser.add_argument("pcap_path", help="Path to the PCAP file")
    parser.add_argument("--report", default="dga_report.csv", help="Path to the output report CSV file")
    parser.add_argument("--plot", action="store_true", help="Generate and display frequency plots for each source IP")
    parser.add_argument("--expected", action="store_true", help="Use expected classification based on extraneous data")
    
    args = parser.parse_args()

    print("Extracting domains and source IPs from PCAP...")
    domain_info = extract_domain_info(args.pcap_path)

    print("Initializing models...")
    pred = predictor()

    print("Analyzing domains...")
    results = analyze_domains(domain_info, pred, args.expected)
    df = pd.DataFrame(results)

    if args.plot:
        print("Generating frequency plots...")
        generate_frequency_graph(df)

    print("Generating report...")
    generate_report(results, args.report)

    print("Creating source IP profiles...")
    profiles = create_source_ip_profiles(df)
    save_profiles_to_csv(profiles, 'source_ip_profiles.csv')

    alert_on_possible_infection(profiles)
