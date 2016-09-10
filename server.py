#!/usr/bin/env python3

from flask import *

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    import sys
    app.run(host="0.0.0.0", port = int(sys.argv[1]) if len(sys.argv) > 1 else 80, threaded=True)
