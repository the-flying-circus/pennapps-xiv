#!/usr/bin/env python3

import requests
import json
import pymongo
import datetime
import xml.etree.ElementTree as ET
from secret import ZWSID, GMAPS_API_KEY, DB_URL
from math import radians, cos, sin, asin, sqrt, pi
from bs4 import BeautifulSoup

def get_mongo_client():
    return pymongo.MongoClient(DB_URL)

def get_crimes(lat, lng):
    client = get_mongo_client()
    out = client.homie.crime.aggregate([
        { "$geoNear": { "near": [lng, lat], "distanceField": "distance", "maxDistance": 10/3959, "spherical": True } },
        { "$match": { "time" : { "$gt": datetime.datetime.now() - datetime.timedelta(days=3*365) } } }
    ])
    client.close()
    return [{ "coord": x["coord"], "type": x["type"], "time": x["time"].isoformat(), "dist": x["distance"]*3959 } for x in out]

def get_crimes_and_collisions(lat, lng):
    out = get_crimes(lat, lng)[:10]
    for x in get_collisions(lat, lng)[:10]:
        out.append({ "coord": x["coord"], "type": "Car Accident", "time": datetime.datetime(x["year"], x["month"], 1).isoformat(), "dist": x["dist"], "car": True })
    out.sort(key=lambda k: k["dist"])
    return out

def get_collisions(lat, lng):
    client = get_mongo_client()
    out = client.homie.collisions.aggregate([
        { "$geoNear": { "near": [lng, lat], "distanceField": "distance", "maxDistance": 10/3959, "spherical": True } },
        { "$match": { "year": { "$gt": datetime.datetime.now().year - 3 } } }
    ])
    client.close()
    return [{ "coord": x["coord"], "year": x["year"], "month": x["month"], "dist": x["distance"]*3959 } for x in out]

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3959
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
        "types": building
    })
    out = r.json()
    if out["status"] != "OK":
        if "ZERO_RESULTS" in out["status"]:
            return { "results": [], "status": "OK" }
        else:
            raise Exception(out["status"])
    return out

def geocode(address):
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params = {
        "key": GMAPS_API_KEY,
        "address": address
    })
    out = r.json()
    if out["status"] != "OK":
        if "ZERO_RESULTS" in out["status"]:
            return { "results": [], "status": "OK" }
        else:
            raise Exception(out["status"])
        raise Exception(out["status"])
    return out

def split_from_geocode(data):
    parts = data["results"][0]["address_components"]
    out = {}
    for part in parts:
        out[next(x for x in part["types"] if x != "political")] = part["long_name"]
    try:
        return "{} {}".format(out["street_number"], out["route"]), "{}, {} {}".format(out["locality"] if "locality" in out else out["sublocality"], out["administrative_area_level_1"], out["postal_code"])
    except KeyError as e:
        return None, None

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
        if msg_code == 502 or msg_code == 504 or msg_code == 506 or msg_code == 507 or msg_code == 508:
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

def get_overview_data(laddr, lzip):
    data = get_zillow_data(laddr, lzip)
    if not data:
        return None
    return {
        "sqft": float(data["finishedSqFt"]),
        "built": int(data["yearBuilt"]),
        "zillow": data["links"]["homedetails"],
        "address": data["address"],
        "bedrooms": data.get("bedrooms", None),
        "bathrooms": data.get("bathrooms", None),
        "lastSold": data.get("lastSoldDate", None),
        "zestimate": float(data["zestimate"]["amount"])
    }

def get_public_services(geoinfo):
    loc = geoinfo["results"][0]["geometry"]["location"]
    data = get_nearby(loc["lat"], loc["lng"], building="hospital|library|book_store|post_office")
    out = []
    for x in data["results"][:10]:
        loc2 = x["geometry"]["location"]
        out.append({
            "name": x["name"],
            "type": type_lookup(x["types"]),
            "dist": haversine(loc["lng"], loc["lat"], loc2["lng"], loc2["lat"])
        })
    return out

def get_parks(geoinfo):
    loc = geoinfo["results"][0]["geometry"]["location"]
    data = get_nearby(loc["lat"], loc["lng"], building="park|zoo|campground")
    out = []
    for x in data["results"][:10]:
        loc2 = x["geometry"]["location"]
        out.append({
            "name": x["name"],
            "type": type_lookup(x["types"]),
            "dist": haversine(loc["lng"], loc["lat"], loc2["lng"], loc2["lat"])
        })
    return out
            
def type_lookup(t):
    if "hospital" in t:
        return "hospital"
    if "bus_station" in t:
        return "bus_station"
    if "subway_station" in t:
        return "subway_station"
    if "library" in t:
        return "library"
    if "book_store" in t:
        return "book_store"
    if "post_office" in t:
        return "post_office"
    if "park" in t:
        return "park"
    if "zoo" in t:
        return "zoo"
    if "campground" in t:
        return "campground"
    return ", ".join(t)

def get_transportation(geoinfo):
    loc = geoinfo["results"][0]["geometry"]["location"]
    data = get_nearby(loc["lat"], loc["lng"], building="bus_station|subway_station")
    out = []
    for x in data["results"][:10]:
        loc2 = x["geometry"]["location"]
        out.append({
            "name": x["name"],
            "type": type_lookup(x["types"]),
            "dist": haversine(loc["lng"], loc["lat"], loc2["lng"], loc2["lat"])
        })
    return out
    
def get_census(address):
    r = requests.get("https://geocoding.geo.census.gov/geocoder/locations/onelineaddress/", params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    })
    print(r.text)
    out = r.json()
    
def get_schools(lat, lng):
    r = requests.get("https://webapps.philasd.org/school_finder/ajax/pip/" + str(lat) + '/' + str(lng))
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.find("dl")
    if not items:
        return None
    items = [x for x in items]
    out = []
    for i in range(0, len(items), 2):
        out.append({ "grade": items[i].text, "name": items[i + 1].text })
    return out

if __name__ == "__main__":
    rawadd = "4224 N Fairhill St, Philadelphia, PA 19140"
    d = geocode(rawadd)
    print(json.dumps(d, indent=4, sort_keys=True))
    loc = d["results"][0]["geometry"]["location"]
    laddr, lzip = split_from_geocode(d)
    # d = get_nearby(loc["lat"], loc["lng"])
    # print(json.dumps(d, indent=4, sort_keys=True))
    # d = get_zillow_data(laddr, lzip, advanced=True)
    # print(json.dumps(d, indent=4, sort_keys=True))
    # d = get_crimes(loc["lat"], loc["lng"])
    # print(json.dumps(d, indent=4, sort_keys=True))
    # d = get_collisions(loc["lat"], loc["lng"])
    # print(json.dumps(d, indent=4, sort_keys=True))
    # d = get_census(rawadd)
    # print(json.dumps(d, indent=4, sort_keys=True))
    d = get_schools(loc["lat"], loc["lng"])
    print(json.dumps(d, indent=4, sort_keys=True))
