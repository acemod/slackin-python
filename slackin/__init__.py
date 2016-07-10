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
import threading

import requests
import docopt

from flask import Flask, render_template, request, send_from_directory, make_response
from werkzeug.contrib.cache import SimpleCache
from htmlmin.minify import html_minify

cache = SimpleCache()
app = Flask(__name__, static_url_path="/static")


def update_data():
    try:
        print("==> Updating team data ...")
        try:
            r = requests.get("https://slack.com/api/team.info", params={
                "token": app.config["token"]})
            j = r.json()
            assert j["ok"]
        except:
            print("    !!! Failed to update team data.")
        else:
            team = j["team"]
            cache.set("team", team)

        print("==> Updating user data ...")
        try:
            r = requests.get("https://slack.com/api/users.list", params={
                "token": app.config["token"],
                "presence": 1})
            j = r.json()
            assert j["ok"]
        except:
            print("    !!! Failed to update user data.")
        else:
            users = [u for u in j["members"] if not u.get("is_bot", False) and not u["deleted"]]
            cache.set("users_total", users)

            active = [u for u in users if u.get("presence", "away") == "active"]
            cache.set("users_active", active)
    except BaseException as e:
        print("!!! Exception in update_data: "+str(e))

    threading.Timer(app.config["interval"] / 1000, update_data).start()


@app.route("/")
def index():
    team = cache.get("team")
    return html_minify(render_template("index.html",
        subdomain=team["domain"],
        logo=team["icon"]["image_132"],
        users_active=len(cache.get("users_active")),
        users_total=len(cache.get("users_total"))))


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
    return html_minify(render_template("iframe.html",
        large="slack-btn-large" if "large" in request.args.keys() else "",
        users_active=len(cache.get("users_active")),
        users_total=len(cache.get("users_total"))))


@app.route("/iframe/dialog")
def dialog():
    team = cache.get("team")
    return html_minify(render_template("dialog.html",
        subdomain=team["domain"],
        users_active=len(cache.get("users_active")),
        users_total=len(cache.get("users_total"))))


@app.route("/badge.svg")
def badge_svg():
    users = len(cache.get("users_total"))
    active = len(cache.get("users_active"))

    label = request.args.get("label", "slack")

    if active > 0:
        value = "{}/{}".format(active, users)
    else:
        value = str(users) if users > 0 else "-"

    left_width = 8 + 7 * len(label)
    right_width = 8 + 7 * len(value)

    try:
        templates = {
            "plastic": "badge.svg",
            "flat": "badge_flat.svg",
            "flat-square": "badge_flat-square.svg"
        }
        template = templates[request.args.get("style", "plastic")]
    except KeyError:
        template = "badge.svg"

    svg = html_minify(render_template(template,
        label=label,
        value=value,
        left_width=left_width,
        right_width=right_width))
    svg = svg.replace("<html><head></head><body>", "")
    svg = svg.replace("</body></html>", "")
    response = make_response(svg)
    response.content_type = 'image/svg+xml'
    return response


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

    update_data()
    app.run(host="0.0.0.0", port=int(args["--port"]), debug=os.environ.get("DEBUG"))
