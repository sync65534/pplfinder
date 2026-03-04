from bs4 import BeautifulSoup
import json
import extractions
import requests
import county

def load_county_list(fname="/home/tris/stalking/county_list.json"):
    a = []
    with open(fname, 'r') as f:
        data = json.load(f)
        for county_name, info in data.items():
            state, data_type, links, notes = info.values()
            a.append(county.County(county_name, state, data_type, links, notes))
    return a
county_list = load_county_list()

data_cases = {
    "WTHGIS": extractions.WTHGIS_extract
}
def find(fname = '', lname = ''):
    collective = {}
    for county in county_list:
        link = county.links[0].replace("LASTNAME", lname).replace("FIRSTNAME", fname)
        resp = requests.get(link).content.decode()
        if county.name == "Marlboro": print(requests.get(link).status_code)
        if county.state not in collective:
            collective[county.state] = {}
        collective[county.state][county.name] = data_cases.get(county.datacase)(resp, county)
    return collective

