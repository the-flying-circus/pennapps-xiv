#!/usr/bin/env python3

import requests
import json
import xml.etree.ElementTree as ET
from secret import ZWSID, GMAPS_API_KEY
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956
    return c * r

def xml_to_dict(xml):
    out = {}
    for x in xml:
        if not x.text:
            out[x.tag] = xml_to_dict(x)
        else:
            out[x.tag] = x.text
    return out

# other values: https://developers.google.com/places/supported_types
def get_nearby(lat, lng, building="bus_station"):
    r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params = {
        "key": GMAPS_API_KEY,
        "rankby": "distance",
        "location": "{},{}".format(lat, lng),
        "type": building
    })
    out = r.json()
    if out["status"] != "OK":
        raise Exception(out["status"])
    return out

def geocode(address):
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params = {
        "key": GMAPS_API_KEY,
        "address": address
    })
    out = r.json()
    if out["status"] != "OK":
        raise Exception(out["status"])
    return out

def split_from_geocode(data):
    parts = data["results"][0]["address_components"]
    out = {}
    for part in parts:
        out[next(x for x in part["types"] if x != "political")] = part["long_name"]
    try:
        return "{} {}".format(out["street_number"], out["route"]), "{}, {} {}".format(out["locality"] if "locality" in out else out["sublocality"], out["administrative_area_level_1"], out["postal_code"])
    except KeyError:
        return None

def get_zillow_data(address, citystatezip, advanced=False):
    r = requests.post("https://www.zillow.com/webservice/GetDeepSearchResults.htm", data = {
        "zws-id": ZWSID,
        "address": address,
        "citystatezip": citystatezip
    })
    root = ET.fromstring(r.text)
    msg = root.find("message")
    msg_code = int(msg.find("code").text)
    if msg_code != 0:
        if msg_code == 502 or msg_code == 504 or msg_code == 506 or msg_code == 507:
            return None
        raise Exception("zillow api error: {} {}".format(msg_code, msg.find("text").text))
    resp = root.find("response").find("results").find("result")
    out = xml_to_dict(resp)
    if advanced:
        r = requests.post("https://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm", data = {
            "zws-id": ZWSID,
            "zpid": int(out["zpid"])
        })
        root = ET.fromstring(r.text)
        msg_code = int(root.find("message").find("code").text)
        if msg_code == 0:
            out["advanced"] = xml_to_dict(root.find("response"))
        else:
            out["advanced"] = None
            out["advanced_error"] = msg_code
    return out

if __name__ == "__main__":
    d = geocode("4224 N Fairhill St, Philadelphia, PA 19140")
    print(json.dumps(d, indent=4, sort_keys=True))
    loc = d["results"][0]["geometry"]["location"]
    laddr, lzip = split_from_geocode(d)
    d = get_nearby(loc["lat"], loc["lng"])
    print(json.dumps(d, indent=4, sort_keys=True))
    d = get_zillow_data(laddr, lzip, advanced=True)
    print(json.dumps(d, indent=4, sort_keys=True))
