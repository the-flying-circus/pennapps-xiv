#!/usr/bin/env python3

from flask import *
import requests
import secret
import data
import datetime
import locale
import traceback

app = Flask(__name__, static_url_path="")
app.secret_key = secret.SECRET_KEY

@app.template_filter()
def format_date(t):
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").strftime("%r %D")

@app.template_filter()
def format_money(m):
    locale.setlocale( locale.LC_ALL, '' )
    return locale.currency(m, grouping=True)

@app.template_filter()
def crop_list(l):
    return l[:min(10, len(l))]

@app.template_filter()
def to_year(d):
    return int(d.split("/")[-1])

@app.route("/")
def index():
    return render_template("index.html", mapskey=secret.GMAPS_FRONT_KEY)

@app.route("/info")
def info():
    address = request.args.get("query")
    import data, secret
    geoinfo = data.geocode(address)
    if geoinfo and len(geoinfo["results"]) > 0:
        laddr, lzip = data.split_from_geocode(geoinfo)
        if laddr and lzip:
            place_id = request.args.get("place_id", geoinfo["results"][0]["place_id"])
            loc = geoinfo["results"][0]["geometry"]["location"]
            lat = loc["lat"]
            lng = loc["lng"]
            try:
                context = {"mapkey": secret.GMAPS_FRONT_KEY,
                           "current_year": datetime.datetime.now().year,
                           "place_id": place_id,
                           "lat": lat,
                           "lng": lng,
                           "overview": data.get_overview_data(laddr, lzip),
                           "services": data.get_public_services(geoinfo),
                           "transportation": data.get_transportation(geoinfo),
                           "crimes": data.get_crimes_and_collisions(lat, lng),
                           "schools": data.get_schools(lat, lng),
                           "parks": data.get_parks(geoinfo),
                           "entertainment": data.get_entertainment(geoinfo),
                           "emergency": data.get_emergency(geoinfo)
                }
            except Exception as e:
                traceback.print_exc()
                flash("Error processing request: {}".format(e))
                return redirect("/")
            return render_template("info.html", **context)
        else:
            flash("Invalid address! We could not find a street address for the location you provided.")
            return redirect("/")
    else:
        flash("Invalid address! We could not geocode the address you provided.")
        return redirect("/")

if __name__ == "__main__":
    import sys
    app.run(host="0.0.0.0", port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080, threaded=True)
