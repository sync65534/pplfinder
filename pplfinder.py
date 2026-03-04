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
            print(links)
            a.append(county.County(county_name, state, data_type, links, notes))
    return a
county_list = load_county_list()

data_cases = {
    "WTHGIS": extractions.WTHGIS_extract
}
def find(name):
    collective = {}
    for county in county_list:
        link = county.links[0].replace("NAMEHERE", name)
        resp = requests.get(link).content.decode()
        collective.update(data_cases.get(county.datacase)(resp, county))
    return json.dumps(collective)
