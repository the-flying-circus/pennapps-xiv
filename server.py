#!/usr/bin/env python3

from flask import *

app = Flask(__name__, static_url_path="")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info")
def info():
    address = request.args.get("query")
    import data
    laddr, lzip = data.split_from_geocode(data.geocode(address))
    context = {"overview": data.get_overview_data(),
               "taxes": data.get_tax_history(),
               "neighborhood": data.get_neighborhood_data(),
               "services": data.get_public_services(),
               "transportation": data.get_transportation(),
    }
    return render_template("info.html", **context)

if __name__ == "__main__":
    import sys
    app.run(host="0.0.0.0", port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080, threaded=True)
