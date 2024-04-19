import csv
import random

#this file is used to generate the Dictionary-based dataset for the isDictDGA model

TOTAL_NUM = 10000

#generate Dictionary-based DGAs using top 3000 words in Oxford dictionary
def generate_domains():

    #open dataset
    with open("./data/The_Oxford_3000.txt", "r") as r:
        #extrac words
        words = [w.strip().split(" ")[0] for w in r.readlines()]


    data = []
    #iterate over how many domains you want
    for c in range(TOTAL_NUM):
        
        first_word = words[random.randint(0, 3000)]
        second_word = words[random.randint(0, 3000)]
        tld = ".net"
        domain = first_word + second_word + tld
        data.append((domain, "DGA"))

    return data

#grab 10000 domains from alexa top domains
def generate_benign():
    with open("./data/alexa-domains.txt", "r") as r:
        words = [w.strip().split(" ")[0] for w in r.readlines()]

    data = []
    for c in range(TOTAL_NUM):
        word = words[c]
        data.append((word, "benign"))
    
    return data

#write all the domains to csv file
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

#main function
if __name__=="__main__":
    dgas = generate_domains()
    benign = generate_benign()
    combined = dgas + benign
    write_csv(combined)
