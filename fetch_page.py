import sys
import urllib.request
import re
from html.parser import HTMLParser

class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.skip_tag = None
        self.body_text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
            
        if tag in ['script', 'style', 'noscript'] and not self.skip_tag:
            self.skip_tag = tag

    def handle_endtag(self, tag):
        if tag == self.skip_tag:
            self.skip_tag = None

    def handle_data(self, data):
        if self.in_body and not self.skip_tag:
            text = data.strip()
            if text:
                self.body_text.append(text)

def fetch_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8', errors='ignore')
        
        p = MyParser()
        p.feed(html)
        return " ".join(p.body_text)
    except Exception as e:
        print("error fetching url:", url)
        return ""

def get_frequencies(text):
    freqs = {}
    
    # regex to get all alphanumeric characters
    # making it lowercase so case doesn't matter
    text = text.lower()
    words = re.findall(r'[a-z0-9]+', text)
    
    for w in words:
        if w in freqs:
            freqs[w] = freqs[w] + 1
        else:
            freqs[w] = 1
            
    return freqs

def rolling_hash(word):
    num_hash = 0
    p = 53
    m = 2 ** 64
    
    for i in range(len(word)):
        ascii_val = ord(word[i])
        term = ascii_val * (p ** i)
        num_hash = (num_hash + term) % m
        
    return num_hash

def get_simhash(freqs):
    v = [0] * 64
    
    for word in freqs:
        weight = freqs[word]
        h = rolling_hash(word)
        
        # treating the hash array as a string of ones and zeroes is easier
        bin_str = bin(h)[2:]
        
        # pad till it's exactly 64 characters long
        while len(bin_str) < 64:
            bin_str = "0" + bin_str
            
        for i in range(64):
            if bin_str[i] == '1':
                v[i] = v[i] + weight
            else:
                v[i] = v[i] - weight
                
    # build the final simhash string
    final_bits = ""
    for num in v:
        if num > 0:
            final_bits += "1"
        else:
            final_bits += "0"
            
    return final_bits

if len(sys.argv) != 3:
    print("usage: python fetch_page.py <url1> <url2>")
    sys.exit(1)

url1 = sys.argv[1]
url2 = sys.argv[2]

text1 = fetch_text(url1)
text2 = fetch_text(url2)

freqs1 = get_frequencies(text1)
freqs2 = get_frequencies(text2)

hash1 = get_simhash(freqs1)
hash2 = get_simhash(freqs2)

common_count = 0
for i in range(64):
    if hash1[i] == hash2[i]:
        common_count += 1
        
print("Common bits:", common_count)
