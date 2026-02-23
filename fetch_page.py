import sys
import urllib.request
from html.parser import HTMLParser

class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_body = False
        self.skip_tag = None
        
        self.title = ""
        self.body_text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        elif tag == 'body':
            self.in_body = True
            
        if tag in ['script', 'style', 'noscript'] and not self.skip_tag:
            self.skip_tag = tag
            
        if tag == 'a':
            for attr, val in attrs:
                if attr == 'href' and val:
                    self.links.append(val)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
            
        if tag == self.skip_tag:
            self.skip_tag = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_body and not self.skip_tag:
            text = data.strip()
            if text:
                self.body_text.append(text)

if len(sys.argv) != 2:
    print("usage: python fetch_page.py <url>")
    sys.exit(1)

url = sys.argv[1]

# adding header because some sites block python bot
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    res = urllib.request.urlopen(req)
    html = res.read().decode('utf-8', errors='ignore')
    
    p = MyParser()
    p.feed(html)
    
    print(p.title.strip())
    print(" ".join(p.body_text))
    
    for link in p.links:
        print(link)
        
except Exception as e:
    print("error fetching url:")
    print(e)

