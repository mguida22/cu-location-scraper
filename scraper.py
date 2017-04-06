import argparse
import json

import requests
from bs4 import BeautifulSoup


COLORADO_MAP_URL = "http://www.colorado.edu/map/"
OSM_URL = "https://nominatim.openstreetmap.org/search?q={}&format=json&viewbox=-105.3,39.96,-105.19,40.05&bounded=1"


def get_building_codes():
    r = requests.get(COLORADO_MAP_URL)

    soup = BeautifulSoup(r.text, "html5lib")
    location_links = soup.find(id="destinations-list").ul.find_all("a")

    codes = []
    for link in location_links:
        code = link.get("href")
        name = link.get_text()
        codes.append((code, name))

    return codes


def get_building_locations(building_codes):
    locations = []
    for code in building_codes:
        r = requests.get(OSM_URL.format(code[0]))
        r = r.json()

        if len(r) > 0:
            r = r[0]

            locations.append({
                "code": code[0],
                "name": code[1],
                "latitude": r["lat"],
                "longitude": r["lon"]
            })
        else:
            # got an empty response
            print(code[0])

    return locations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CU location scraper")

    parser.add_argument("--outfile", type=str, default="locations.json",
                        help="Filename to save locations to")
    parser.add_argument("--pretty-print", action="store_true",
                        help="Pretty print json output")

    args = parser.parse_args()

    building_codes = get_building_codes()
    building_locations = get_building_locations(building_codes)

    with open(args.outfile, "w") as outfile:
        if args.pretty_print:
            json.dump(building_locations, outfile, indent=4)
        else:
            json.dump(building_locations, outfile)

    print("Scraped and saved {} locations to {}".format(
        len(building_locations), args.outfile))
