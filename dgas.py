import random
import time
import base64
from ctypes import c_uint 
from itertools import product
import socket
from datetime import datetime, timedelta

############################################################################ NON DICTIONARY DGAs #########################################################

# generates a LOT of .bazar domains
def bazarDGA():
    domain_list = []
    d = datetime.now()
    month = d.month
    year = d.year
    date_str = "{0:02d}{1:04d}".format(12-month, year-18)

    valid_chars = [
      "abcde",
      "cdef",
      "efgh",
      "ghi",
      "ijk",
      "klm"
    ]
    valid_chars = [list(_) for _ in valid_chars]
    for part1 in product(*valid_chars):
        domain = "".join(part1)
        for i, c in enumerate(part1):
            domain += chr(ord(c) + int(date_str[i]) )
        domain += ".bazar"
        domain_list.append(domain)
    return domain_list

#https://github.com/pchaigno/dga-collection/blob/master/dgacollection/Cryptolocker.py
def cryptolockerDGA():
    tlds = ["com", "net", "biz", "ru", "org", "co.uk", "info"]
    domain_list = []
    date = datetime.now()
    y, m, d = date.year, date.month, date.day

    for _ in range(40):
      d *= 65537
      m *= 65537
      y *= 65537
      
      s = d >> 3 ^ y >> 8 ^ y >> 11
      s &= 3
      s += 12

      n = ""
      for i in range(s):
        d = ((d << 13 & 0xFFFFFFFF) >> 19 & 0xFFFFFFFF) ^ ((d >> 1 & 0xFFFFFFFF) << 13 & 0xFFFFFFFF) ^ (d >> 19 & 0xFFFFFFFF)
        d &= 0xFFFFFFFF
        m = ((m << 2 & 0xFFFFFFFF) >> 25 & 0xFFFFFFFF) ^ ((m >> 3 & 0xFFFFFFFF) << 7 & 0xFFFFFFFF)  ^ (m >> 25 & 0xFFFFFFFF)
        m &= 0xFFFFFFFF
        y = ((y << 3 & 0xFFFFFFFF) >> 11 & 0xFFFFFFFF) ^ ((y >> 4 & 0xFFFFFFFF) << 21 & 0xFFFFFFFF) ^ (y >> 11 & 0xFFFFFFFF)
        y &= 0xFFFFFFFF
        
        n += chr(ord('a') + (y ^ m ^ d) % 25)

      domain = n + "." + tlds[i % 7]
      domain_list.append(domain)

    return domain_list

# https://github.com/baderj/domain_generation_algorithms/blob/master/dmsniff/dga.py
def dmsniffDGA():
    domain_list = []
    domain = random.choice(["sn", "al"])
    if domain == "sn":
        primes = [1,7,3,5,11,13]
    else:
        primes = [1,3,5,7,11,13]
    for nr in range(1,51):
        for prime in primes: 
            domain += chr(half_until_smaller_equal_24((prime*nr)) + ord('a'))
        domain += [".com", ".org", ".net", ".ru", ".in"][half_until_smaller_equal_24(nr)%5]
        nr += 1
        domain_list.append(domain)
    return domain_list

def half_until_smaller_equal_24(nr):
    while nr > 24:
        nr = nr >> 1
    return nr

#https://github.com/baderj/domain_generation_algorithms/blob/master/sisron/dga.py
def sisronDGA():
    domain_list = []
    d = datetime.now()
    for i in range(40):
        day_index = i%10
        tld_index = i//10
        tlds = [x.encode('ascii') for x in [".com", ".org", ".net", ".info"]]
        d -= timedelta(days=day_index)
        ds = d.strftime("%d%m%Y").encode('latin1')
        domain = base64.b64encode(ds).lower().replace(b"=",b"a") + tlds[tld_index]
        domain_list.append(domain.decode('latin1'))
    return domain_list

############################################################################ DICTIONARY DGAs #########################################################

def suppoboxDGA():
    domain_list = []
    time_ = datetime.now()
    timeint = int(time_.strftime('%Y%m%d'))
    with open("./dict_dga_wordlists/words1.txt", "r") as r:
        words = [w.strip() for w in r.readlines()]

    seed = int(timeint) >> 9
    for c in range(85):
        nr = seed
        res = 16*[0]
        shuffle = [3, 9, 13, 6, 2, 4, 11, 7, 14, 1, 10, 5, 8, 12, 0]
        for i in range(15):
            res[shuffle[i]] = nr % 2
            nr = nr >> 1

        first_word_index = 0
        for i in range(7):
            first_word_index <<= 1
            first_word_index ^= res[i]

        second_word_index = 0
        for i in range(7,15):
            second_word_index <<= 1
            second_word_index ^= res[i]
        second_word_index += 0x80

        first_word = words[first_word_index]
        second_word = words[second_word_index]
        tld = ".net"
        domain_list.append("{}{}{}".format(first_word, second_word, tld))
        seed += 1
    return domain_list

#https://github.com/baderj/domain_generation_algorithms/blob/master/gozi/dga.py
class Rand:
    def __init__(self, seed):
        self.r = c_uint(seed) 
    def rand(self):
        self.r.value = 1664525*self.r.value + 1013904223
        return self.r.value

seeds = {
        'luther': {'div': 4, 'tld': '.com', 'nr': 12},
        'rfc4343': {'div': 3, 'tld': '.com', 'nr': 10},
        'nasa': {'div': 5, 'tld': '.com', 'nr': 12},
        'gpl': {'div': 5, 'tld': '.ru', 'nr': 10}
        }

def get_words(wordlist):
    with open(wordlist, 'r') as r:
        return [w.strip() for w in r if w.strip()]

def goziDGA():
    domain_list = []
    date = datetime.now()
    wordlist = 'luther'

    words = get_words('./dict_dga_wordlists/'+wordlist+'.txt')
    diff = date - datetime.strptime("2015-01-01", "%Y-%m-%d")
    days_passed = (diff.days // seeds[wordlist]['div'])
    flag = 1
    seed = (flag << 16) + days_passed - 306607824
    r = Rand(seed) 

    for i in range(16):
        r.rand()
        v = r.rand()
        length = v % 12 + 12
        domain = ""
        while len(domain) < length:
            v = r.rand() % len(words)
            word = words[v] 
            l = len(word)
            if not r.rand() % 3:
                l >>= 1
            if len(domain) + l <= 24:
                domain += word[:l]
        domain += seeds[wordlist]['tld']
        domain_list.append(domain)
    return domain_list

# https://github.com/baderj/domain_generation_algorithms/blob/master/banjori/example_domains.txt
def map_to_lowercase_letter(s):
    return ord('a') + ((s - ord('a')) % 26)

def banjoriDGA():
    domain_list = []
    seed = 'earnestnessbiophysicalohax.com'
    domain = seed
    for i in range(50):
        dl = [ord(x) for x in list(domain)]
        dl[0] = map_to_lowercase_letter(dl[0] + dl[3])
        dl[1] = map_to_lowercase_letter(dl[0] + 2*dl[1])
        dl[2] = map_to_lowercase_letter(dl[0] + dl[2] - 1)
        dl[3] = map_to_lowercase_letter(dl[1] + dl[2] + dl[3])
        domain = ''.join([chr(x) for x in dl])
        domain_list.append(domain)
    return domain_list
