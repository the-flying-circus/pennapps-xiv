#!/usr/bin/env python3

import requests
import json
import xml.etree.ElementTree as ET
from secret import ZWSID

def xml_to_dict(xml):
    out = {}
    for x in xml:
        if not x.text:
            out[x.tag] = xml_to_dict(x)
        else:
            out[x.tag] = x.text
    return out

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
    d = get_zillow_data("4224 N Fairhill St", "Philadelphia, PA 19140", advanced=True)
    print(json.dumps(d, indent=4, sort_keys=True))
