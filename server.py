#!/usr/bin/env python3

from flask import *
import requests
import secret
import data

app = Flask(__name__, static_url_path="")
app.secret_key = secret.SECRET_KEY

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info")
def info():
    address = request.args.get("query")
    import data, secret
    geoinfo = data.geocode(address)
    laddr, lzip = data.split_from_geocode(geoinfo)
    if laddr and lzip:
        r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params = {
            "query": address,
            "key": secret.GMAPS_PLACES_KEY
        })
        place_id = r.json()["results"][0]["place_id"]
        context = {"mapkey": secret.GMAPS_EMBED_KEY,
                   "place_id": place_id,
                   "overview": data.get_overview_data(laddr, lzip),
                   "taxes": data.get_tax_history(),
                   "neighborhood": data.get_neighborhood_data(),
                   "services": data.get_public_services(geoinfo),
                   "transportation": data.get_transportation(geoinfo),
        }
        return render_template("info.html", **context)
    else:
        flash("Invalid address!")
        return redirect("/")

if __name__ == "__main__":
    import sys
    app.run(host="0.0.0.0", port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080, threaded=True)
