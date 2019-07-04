#!/usr/bin/env python3
#
# Slack alert script for Pushover
# (c) 2016, Entertainment Media Group AG
# License: MIT
#

# Standard Library
import json
import os
import os.path
import re
import urllib
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from configparser import RawConfigParser
from sys import exit, stderr

# First Party
import httplib2
from dotenv import load_dotenv


# Load the .env
load_dotenv()

try:
    os.environ["SLACK_WEBHOOK_URL"]
    os.environ["SLACK_USERNAME"]
    os.environ["ICON_EMOJI"]
    good = "\[OK\]"
    warning = "\[Problem\] \((Warning|Average)\)"
    danger = "\[Problem\] \((High|Critical)\)"
except:
    print("Variables are missing!")

# parse cli argumennts
parser = ArgumentParser(
    description="Zabbix Slack Client", formatter_class=ArgumentDefaultsHelpFormatter
)
parser.add_argument("to", help="Receiving user or channel")
parser.add_argument("subject", help="Message subject")
parser.add_argument("message", help="Message body")
args = parser.parse_args()


# determine message color
color = "none"
if good and re.match(good, args.subject):
    color = "good"
elif warning and re.match(warning, args.subject):
    color = "warning"
elif danger and re.match(danger, args.subject):
    color = "danger"

# send API request
options = {
    "attachments": [
        {
            "fallback": args.subject + "\n" + args.message,
            "color": color,
            "title": args.subject,
            "text": args.message,
        }
    ],
    "username": os.environ["SLACK_USERNAME"],
    "icon_emoji": os.environ["ICON_EMOJI"],
}

conn = httplib2.HTTPSConnectionWithTimeout("hooks.slack.com:443")
conn.request(
    "POST",
    f"/services/{os.environ['SLACK_WEBHOOK_URL']}",
    json.dumps(options),
    {"Content-type": "application/json"},
)

res = conn.getresponse()

if res.status != 200:
    print("Slack API returned error: " + res.read(), end="\n", file=stderr)
    exit(1)
