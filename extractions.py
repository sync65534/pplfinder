import re
def WTHGIS_extract(responce, county):
    cdata_match = re.search(r"<!\[CDATA\[(.*?)\]\]>", responce, re.DOTALL)
    if not cdata_match:
        return [], []

    html_fragment = cdata_match.group(1)

    pattern = re.compile(
    r"<div\s+id=oli\d+\s+onclick='showf\(\s*46\s*,\s*(\d+)\s*\)'></div>"
    r"<button\s+id=btnViewPropertyRecordCard\s+onclick='printPropertyRecordCard\(\s*46\s*,\s*\1\s*\)'>Card</button>"
    r"<button\s+id=btnZoomToParcel\s+onclick='showf\(\s*46\s*,\s*\1\s*\)'>Zoom</button>"
    r"</div><div\s+id=resultsParcelNumber\s+class='mainResultItem'>.*?</div>"
    r"<div\s+class='secondaryResultItem'>([^<]+)</div>",
    re.DOTALL
    )
    matches = pattern.findall(html_fragment)

    results = {name.strip(): county.links[1].replace("VALUEHERE", str(int(x))) for x, name in matches}

    return results



