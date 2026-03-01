import requests
import pandas as pd
import pprint
import csv
from bs4 import BeautifulSoup
import re


class county:
    def __init__(self, name, state, link, datacase, notes):
        self.name = name
        self.state = state
        self.link = link
        self.datacase = datacase
        self.notes = notes
    def __repr__(self):
        return self.name
# make and fill county list
county_list = []

with open("county_list.csv", 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    for line in reader:
        name, state, link, datacase, notes = line
        county_list.append(county(name, state, link, datacase, notes)) 

# def data cases
def extract_cdata_content(text):
    cdata_match = re.search(r"<!\[CDATA\[(.*?)\]\]>", text, re.DOTALL)
    html_block = cdata_match.group(1)

    soup = BeautifulSoup(html_block, "html.parser")

    names = [
        div.get_text(strip=True)
        for div in soup.find_all("div", class_="secondaryResultItem")
    ]
    names = [ name for name in names if name.find("Owner Address") == -1 and name.find("Property Address") == -1]
    return names
case_dict = {
    "CDATA": extract_cdata_content
}

# func to find the thingy
def find(name):
    for county in county_list:
        link = county.link
        link = link.replace("NAMEHERE", name)
        r = requests.get(link)
    print(link)
    return case_dict.get(county.datacase)(r.content.decode())

