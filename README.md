slackin-python
==============

This is a Python port of the [slackin](https://github.com/rauchg/slackin) project.


## Setup

```
# python3 setup.py install
```


## Usage

```
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
```


## Limitations

Things that aren't implemented right now:

- Live Updates
- Channel Limitation
