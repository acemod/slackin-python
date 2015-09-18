#!/usr/bin/env python3

"""
slackin - Slack invite generator

Usage:
    slackin [-p <port>] [-i <ms>] [-c <channels>] <slack-subdomain> <api-token>
    slackin (-h | --help)
    slackin (-v | --version)

Options:
    <slack-subdomain>        The name/subdomain of your team
    <api-token>              An authorized API token
    -h --help                Output usage information
    -v --version             Output the version number
    -p --port <port>         Port to listen on (default: 3000)
    -c --channels <channels> Comma-seperated list of channels
    -i --interval <ms>       How frequently to poll Slack (default: 1000)
"""

VERSION = "v1.0"


import os
import sys
import json
import time
import copy
import uuid

import requests
import docopt

from flask import Flask, render_template, request, send_from_directory, make_response
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()
app = Flask(__name__, static_url_path="/static")


def get_data():
    team = cache.get("team")
    if team is None:
        print("==> Updating team data ...")
        r = requests.get("https://slack.com/api/team.info", params={
            "token": app.config["token"]})
        j = r.json()
        assert j["ok"]
        team = j["team"]
        cache.set("team", team, timeout=(app.config["interval"] / 1000))

    users = cache.get("users")
    if users is None:
        print("==> Updating user data ...")
        r = requests.get("https://slack.com/api/users.list", params={
            "token": app.config["token"],
            "presence": 1})
        j = r.json()
        assert j["ok"]
        users = j["members"]
        cache.set("users", users, timeout=(app.config["interval"] / 1000))

    return team, users


@app.route("/")
def index():
    team, users = get_data()

    users = [u for u in users if not u.get("is_bot", False) and not u["deleted"]]
    active = [u for u in users if u["presence"] == "active"]

    return render_template("index.html",
        subdomain=team["domain"],
        logo=team["icon"]["image_132"],
        users_active=len(active),
        users_total=len(users))


@app.route("/invite", methods=["POST"])
def invite():
    if "@" not in request.json["email"]:
        return "missing email", 400
    r = requests.post("https://slack.com/api/users.admin.invite", data={
        "token": app.config["token"],
        "email": request.json["email"]})
    assert r.json()["ok"]
    return "success"


@app.route("/slackin.js")
def badge_js():
    return app.send_static_file("badge.js") 


@app.route("/iframe")
def iframe():
    team, users = get_data()

    users = [u for u in users if not u["is_bot"] and not u["deleted"]]
    active = [u for u in users if u["presence"] == "active"]

    return render_template("iframe.html",
        large="slack-btn-large" if "large" in request.args.keys() else "",
        users_active=len(active),
        users_total=len(users))


@app.route("/iframe/dialog")
def dialog():
    team, users = get_data()

    users = [u for u in users if not u["is_bot"] and not u["deleted"]]
    active = [u for u in users if u["presence"] == "active"]

    return render_template("dialog.html",
        subdomain=team["domain"],
        users_active=len(active),
        users_total=len(users))


@app.route("/badge.svg")
def badge_svg():
    _, users = get_data()

    users = [u for u in users if not u["is_bot"] and not u["deleted"]]
    active = [u for u in users if u["presence"] == "active"]
    users, active = len(users), len(active)

    if active > 0:
        value = "{}/{}".format(active, users)
    else:
        value = str(users) if users > 0 else "-"

    left_width = 47
    right_width = 12 + len(value) * 7

    svg = render_template('badge.svg',
        value=value,
        left_width=left_width,
        right_width=right_width,
        total_width=(left_width + right_width),
        left_x=round(left_width / 2),
        right_x=round(right_width / 2) + left_width)
    response = make_response(svg)
    response.content_type = 'image/svg+xml'
    return response


@app.route("/socket.io/")
def socket():
    return "", 501
    # not implemented because i cannot be arsed
    # also because flask_socketio doesn't support Py3


def main():
    args = docopt.docopt(__doc__, version=VERSION)
    if args["--port"] is None:
        args["--port"] = 3000
    if args["--interval"] is None:
        args["--interval"] = 1000
    
    app.config["token"] = args["<api-token>"]
    app.config["team"] = args["<slack-subdomain>"]
    app.config["interval"] = int(args["--interval"])
    #app.config["channels"] = args["--channels"]
    # also not implemented because i cannot be arsed

    app.run(host="0.0.0.0", port=int(args["--port"]), debug=os.environ.get("DEBUG"))
