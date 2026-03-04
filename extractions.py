import re
from bs4 import BeautifulSoup
def WTHGIS_extract(responce, county):
    cdata_match = re.search(r"<!\[CDATA\[(.*?)\]\]>", responce, re.DOTALL)
    if not cdata_match:
        return [], []
    html_fragment = cdata_match.group(1)
    pattern = re.compile(
        r"showf\(\s*\d+\s*,\s*(\d+)\s*\)"   # capture X
        r".*?"
        r"<div\s+class='secondaryResultItem'>([^<]+)</div>",  # capture name
        re.DOTALL
    )
    matches = pattern.findall(html_fragment)
    results = {name.strip(): county.links[1].replace("VALUEHERE", str(int(x))) for x, name in matches}
    return results



