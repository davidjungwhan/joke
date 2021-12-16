from flask import Flask, render_template, request

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.parse, urllib.request, urllib.error, json

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# By default, App Engine will look for an app called `app` in `main.py`.
app = Flask(__name__)


# Functions
def getjokedata(category = ["Any"], type = ["single"], contains = None, amount = 1):
    request = "https://v2.jokeapi.dev/joke/"

    if len(category) > 1:
        request = request + category[0]
        for item in category[1:]:
            request = request + "," + item
    else:
        if len(category):
            request = request + category[0]
        else:
            request = request + "Any"

    if len(type) == 1:
        request = request + "?type=" + type[0]

    if contains != None:
        request = request + "&contains=" + contains

    if amount != 1:
        request = request + "&amount=" + str(amount)
    requeststr = urllib.request.urlopen(request).read()
    jokedata = json.loads(requeststr)
    return jokedata

def getjokedata_safe(category = ["Any"], type = ["single"], contains = None, amount = 1):
    try:
        return getjokedata(category, type, contains, amount)
    except Exception as error:
        if hasattr(error, "code"):
            print("There was an error with this request. Error code: " + str(error.code))

def joker(category = ["Any"], type = ["single"], contains = None, amount = 1):
    # if amount isn't 1
    if amount != 1:
        joke = getjokedata_safe(category, type, contains, amount)
        if "twopart" in type:
            jokes = ""
            for item in joke["jokes"]:
                jokes = jokes + item["setup"] + "\n" + item["delivery"] + "\n\n"
            return jokes
        else:
            jokes = ""
            for item in joke["jokes"]:
                jokes = jokes + item["joke"] + "\n"
            return jokes

    # if amount is 1
    if "twopart" in type:
        joke = getjokedata_safe(category, type, contains, amount)
        return joke["setup"] + "\n" + joke["delivery"]
    else:
        return getjokedata_safe(category, type, contains, amount)["joke"]


@app.route("/")
def tellajoke():
    title = "A Joke"
    joke = joker()
    return render_template('templates.html', title=title, joke=joke, category=[])


@app.route("/filter")
def filter_handler():
    filter_types = request.args.getlist('filter_type')
    joke = joker(category=filter_types)
    title = "A Joke"
    return render_template('templates.html', title=title, joke=joke, category=filter_types)

if __name__ == "__main__":
    # Used when running locally only.
    # When deploying to Google AppEngine, a webserver process will
    # serve your app.
    app.run(host="localhost", port=8080, debug=True)