# DGA_Project_InfoSec

## Getting Started

Here you will find the setup and evaluation procedures for a system designed to detect Domain Generation Algorithms (DGAs) within network traffic. This project involves generating synthetic network traffic, analyzing it using several machine learning models to detect DGA activities, and visualizing the results.

### Prerequisites

- Python 3.6 or higher
- Libraries: Scapy, Pandas, Matplotlib, NumPy
- Linux or macOS with administrative access

## Installation

Before generating and analyzing network traffic, ensure that all dependencies are installed.

1. **Clone the repository** and navigate to the project directory:
   ```bash
   git clone https://github.com/tobyplw/DGA_Project_InfoSec.git
   cd DGA_Project_InfoSec
2. Run the bash script to install dependencies
    ```bash
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
## Generating Synthetic PCAP Files
pcap_gen.py is used to generate synthetic PCAP files that simulate both benign and malicious (DGA) network traffic.

## Running pcap_gen.py
Ensure all dependencies are installed by running the installation script as mentioned in the Installation section.
Generate the PCAP files:


    python3 pcap_gen.py

This script generates two files: synthetic_traffic.pcap and synth_traffic_non_dga.pcap, containing simulated DGA and benign traffic, respectively.

## Setup and Usage
Run the analysis by specifying the path to the PCAP file along with optional flags to control the output:

    python3 main.py --pcap_path "path_to_pcap_file.pcap" --report --plot

--pcap_path: Path to the pcap file.

--report: Generates a CSV report of the analysis.

--plot: Produces frequency plots of detected DGA queries.

--expected: Uses predefined classifications based on extraneous data for comparison. Use this only for evaluation, ensure that any PCAP you provide includes extraneous data for each packet that includes '4E4F4E' for NON DGA queries and '444741' for DGA queries

# Alerting for DGA Traffic

The system includes a feature to alert users when potential DGA-related malware activity is detected in network traffic.

## Alert Mechanism

When running `main.py`, the script assesses the likelihood of DGA activity based on the analysis and flags any source IP that exceeds a predefined threshold.

## Customizing the Alert Threshold

By default, the system uses a 50% likelihood threshold to trigger an alert. However, you can modify this threshold to suit the specific needs or sensitivity of your network environment.

To change the alert threshold, navigate to the `main.py` script and locate the `alert_on_possible_infection` function. Within this function, adjust the `threshold` parameter to your desired value.

## Analyzing Output
CSV Report: Check the generated dga_report.csv for a detailed report on each analyzed domain. Also, check source_ip_profiles.csv for a report on each profile.

Graphs: View the frequency graphs generated during the analysis to visually assess the DGA detection over time. This will automatically pop up after running main.py and providing the --plot flag.

## Evaluating System Performance
To evaluate the system's performance, you can compare the output against known benchmarks or expected results:

Expected Classification: With the --expected flag, the script classifies based on predefined extraneous data, ideal for validating the model against known outcomes.

Visual Comparison: Use the generated plots to visually compare the frequency of DGA queries in malicious versus benign traffic.
