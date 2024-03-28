import argparse
from scapy.all import rdpcap, DNSQR
import pandas as pd
from predict import predictor

def extract_domains_from_pcap(pcap_path):
    packets = rdpcap(pcap_path)
    domains = set()
    for packet in packets:
        if packet.haslayer(DNSQR):
            domain = packet[DNSQR].qname.decode("utf-8").rstrip('.')
            domains.add(domain)
    return list(domains)

def analyze_domains(domains, pred):
    results = {'domain': [], 'isDGA': [], 'isDictDGA': []}
    for domain in domains:
        isDGA = pred.predict_isDga(domain)
        isDictDGA = pred.predict_isDictDga(domain)
        results['domain'].append(domain)
        results['isDGA'].append(isDGA)
        results['isDictDGA'].append(isDictDGA)
    return results

def generate_report(results, report_path):
    df = pd.DataFrame(results)
    df.to_csv(report_path, index=False)
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a PCAP file for DGA domains.")
    parser.add_argument("pcap_path", help="Path to the PCAP file")
    parser.add_argument("--report", default="dga_report.csv", help="Path to the output report CSV file")
    
    args = parser.parse_args()
    
    print("Extracting domains from PCAP...")
    domains = extract_domains_from_pcap(args.pcap_path)
    
    print("Initializing models...")
    pred = predictor()
    
    print("Analyzing domains...")
    results = analyze_domains(domains, pred)
    
    print("Generating report...")
    generate_report(results, args.report)
