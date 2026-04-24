import pandas as pd
import numpy as np
import requests
import json
from bs4 import BeautifulSoup
import sys
import time
import random
import re
import os

os.makedirs('output', exist_ok=True)

headers = {'user-agent': f'Tianyin class practice(qhh3bv@virginia.edu) (Language={sys.version})'} # example headre based on AWS

# r = requests.get(url, headers=headers)

base_url = "https://sacred-texts.com/ich/"
r = requests.get(base_url, headers=headers)
r.text[:1000]

iching = BeautifulSoup(r.text, features='html.parser')

index = iching.find_all('a', href = lambda x: x and x.startswith('ic'))[7:] # left out intro and plates
index_desc = [i.get_text(strip=True) for i in index]
cont_link = [i['href'] for i in index]
chaps = index_desc[:64]
chaps_link = cont_link[:64]
len(chaps_link)

# ----------------------
# section test
test = cont_link[2]
test_url = base_url + test
tr = requests.get(test_url, headers=headers)
tr2 = re.sub(r'</?[Ii]>', '', tr.text)
tcon = BeautifulSoup(tr2, features='html.parser')

# hex = base_url + tcon.find_all('img')[1]['src']
img = tcon.find('img', src=lambda s: s and 'hex' in s)['src']
plist = tcon.find_all('p')

# [line.string for line in plist]
content = " ".join(p.get_text(strip=True) for p in plist if p.get_text(strip=True))

#---------------------------w
# setup function for scraping

def spider(c_url):
    '''
    Extract Content from each chapter url
    - img, hexagram, link
    - content, chapter contents, string
    '''
    cr = requests.get(c_url, headers = headers)
    cr2 = re.sub(r'</?[Ii]>', '', cr.text)
    cont = BeautifulSoup(cr2, features= 'html.parser')

    # getting Hexagram
    try:
        img = cont.find('img', src=lambda s: s and 'hex' in s)['src']
        hexagram = base_url + img
    except:
        hexagram = None

    # getting page content
    plist = cont.find_all('p')
    content = " ".join(p.get_text(strip=True) for p in plist if p.get_text(strip=True))


    # combine result
    result = {
        "hexagram": hexagram,
        "content": content
        }
    return result


rows = []
for n, c in enumerate(chaps_link):
    print(f"Extracting {c}: {chaps[n]}")
    c_url = base_url + c
    data = spider(c_url)
    rows.append(data)

    # Random delay between requests — key to avoiding rate limiting
    delay = random.uniform(5, 10)
    print(f"  Waiting {delay:.1f}s...")
    time.sleep(delay)

print(f"\nDone! Scraped {len(rows)} pages.")

# ------------------------------------------------------
# Build one table from scraped records + index metadata
df = pd.DataFrame(rows)
df["title"] = chaps
df["url"] = [base_url + i for i in chaps_link]
df = df[["title", "url", "hexagram", "content"]]

df["content"] = (
    df["content"]
    .str.replace(r"\bp\.\s*\d+\b", "", regex=True, case=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df

df['count']= df["content"].fillna("").str.split().str.len()

df.to_csv('output/i_ching_data.csv') # export result

num_docs = len(df)
avg_length = df['count'].mean()
max_length = df['count'].max()
min_length = df['count'].min()

doc_max = df.loc[df['count'].idxmax(), 'title']
doc_min = df.loc[df['count'].idxmin(), 'title']

OHCO = ['chap_num','sent_num', 'token_num']



print("--- I CHING CORPUS SUMMARY ---")
print(f"Total Documents: {num_docs}")
print(f"Average Document Length: {avg_length:.2f} words")
print(f"Maximum Length: {max_length} words ({doc_max})")
print(f"Minimum Length: {min_length} words ({doc_min})")
print(f"The OHCO structure of the corpus is : {OHCO})")