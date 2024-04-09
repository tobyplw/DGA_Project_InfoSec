"""
    generate domains according to: 
    - https://www.endgame.com/blog/malware-with-a-personal-touch.html
    - http://www.rsaconference.com/writable/presentations/file_upload/br-r01-end-to-end-analysis-of-a-domain-generating-algorithm-malware-family.pdf 

"""
import time
from datetime import datetime
import argparse
import csv
import random

TOTAL_NUM = 10000

def generate_domains():
    with open("./data/The_Oxford_3000.txt", "r") as r:
        words = [w.strip().split(" ")[0] for w in r.readlines()]


    data = []
    for c in range(TOTAL_NUM):
        
        first_word = words[random.randint(0, 3000)]
        second_word = words[random.randint(0, 3000)]
        tld = ".net"
        domain = first_word + second_word + tld
        data.append((domain, "DGA"))

    return data

    
def generate_benign():
    with open("./data/alexa-domains.txt", "r") as r:
        words = [w.strip().split(" ")[0] for w in r.readlines()]

    data = []
    for c in range(TOTAL_NUM):
        word = words[c]
        data.append((word, "benign"))
    
    return data

def write_csv(data):
    # File name for the CSV file
    filename = './data/Dict_DGAs_Dataset.csv'

    # Writing data to CSV file
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["domain", "isDGA"])
        # Write data to CSV file
        csvwriter.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")


if __name__=="__main__":
    dgas = generate_domains()
    benign = generate_benign()
    combined = dgas + benign
    write_csv(combined)
