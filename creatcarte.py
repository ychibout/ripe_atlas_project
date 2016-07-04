from __future__ import print_function
import subprocess
from collections import namedtuple
from ripe.atlas.cousteau import AtlasRequest
from pymongo import MongoClient
import time
import datetime
from tkinter import *
import shlex


client = MongoClient('mongodb://localhost')

class Map(object):
    def __init__(self):
        self.active = []
        self.inactive = []
    def add_point(self, coordinates, status):
        if status == 1:
            self.active.append(coordinates)
        else:
            self.inactive.append(coordinates)
    def __str__(self):
        markersCode1 = "\n".join(
            [ """new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                map: map
                }});""".format(lat=x[0], lon=x[1]) for x in self.active
            ])
        markersCode2 = "\n".join(
            [ """new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                map: map
                }});""".format(lat=x[0], lon=x[1]) for x in self.inactive
            ])
        return """
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDN7jkdXxXCQrDfsuel6kciz8p9F6LzqBc"></script>
            <div id="map-canvas" style="height: 100%; width: 100%"></div>
            <script type="text/javascript">
                var map;
                function show_map() {{
                    map = new google.maps.Map(document.getElementById("map-canvas"), {{
                        zoom: 3,
                        center: new google.maps.LatLng(48.8589713, 2.0673746)
                    }});
                    {markersCode1}
                    {markersCode2}
                }}
                google.maps.event.addDomListener(window, 'load', show_map);
            </script>
        """.format(markersCode1=markersCode1, markersCode2=markersCode2)

def recupresultasn(asn) :
    map = Map()
    db = client.bdd
    collection = db.probes

    for elem in collection.find():
        if str(elem["asn"]) == asn:
            if elem["status"] == 1 or elem["status"] == "connect":
                map.add_point((elem["latitude"], elem["longitude"]), 1)
            if elem["status"] == 2 or elem["status"] == "disconnect":
                map.add_point((elem["latitude"], elem["longitude"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)


def listeprobe() :
    db = client.bdd
    collection = db.probes
    i = 0
    while i <= 18500:
        request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&offset=" + str(i)})
        result = namedtuple('Result', 'success response')
        (is_success, response) = request.get()

        for id in response["objects"]:
            collection.insert_one(
                {
                    "id" : id["id"],
                    "status" : id["status"],
                    "timestamp" : id["last_connected"],
                    "latitude" : id["latitude"],
                    "longitude" : id["longitude"],
                    "controller" : "null",
                    "asn" : id["asn_v4"],
                    "country_code" : id["country_code"]
                }
            )

        i+=500

def listeprobeasn(asn):
    db = client.bdd
    collection = db.probes
    request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&asn=" + asn})
    result = namedtuple('Result', 'success response')
    (is_success, response) = request.get()

    for id in response["objects"]:
        collection.insert_one(
            {
                "id" : id["id"],
                "status" : id["status"],
                "timestamp" : id["last_connected"],
                "latitude" : id["latitude"],
                "longitude" : id["longitude"],
                "controller" : "null",
                "asn" : id["asn_v4"],
                "country_code" : id["country_code"]
            }
        )

def outmap() :
    map = Map()
    db = client.bdd
    collection = db.probes

    for elem in collection.find():
            if elem["status"] == "connect" or elem["status"] == 1:
                map.add_point((elem["latitude"], elem["longitude"]), 1)
            if elem["status"] == "disconnect" or elem["status"] == 2:
                map.add_point((elem["latitude"], elem["longitude"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)

def analyse():
        db = client.bdd
        collection = db.probes
        print("à " + datetime.datetime.fromtimestamp(time.time()))
        print("Dernier timestamp :  " + datetime.datetime.fromtimestamp(db.probes.find_one({"$query":{},"$orderby":{"timestamp":-1}})["timestamp"]).strftime('%c') + "\n")
        print("Pays en panne : ")
        for res in collection.distinct("country_code"):
            if collection.count({"country_code" : res}) >= 3 and (collection.count({"country_code" : res, "status" : "disconnect"}) / collection.count({"country_code" : res})) > 0.9 :
                print("\t" + res + " down : " + str(collection.count({"country_code" : res, "status" : "disconnect"})) + " sonde(s)sur " + str(collection.count({"country_code" : res})) + " déconnectée(s)")
        print("Controllers en panne : ")
        for res in collection.distinct("controller"):
            if collection.count({"controller" : res}) >= 3 and (collection.count({"controller" : res, "status" : "disconnect"}) / collection.count({"controller" : res})) > 0.9 :
                print("\tcontroller " + res + " down : " + str(collection.count({"controller" : res, "status" : "disconnect"})) + " sonde(s) sur " + str(collection.count({"controller" : res})) + " déconnectée(s)")
        print("\n")



print("Choisir un asn comme filtre : ")
asn = input(" >> ")

listeprobe()
print("base ok")
subprocess.Popen("xterm -e 'node ~/Documents/Stage_2016/stream/servermongoose.js'", shell=True)
subprocess.call("chromium-browser ~/Documents/Stage_2016/stream/socketapi.html", shell=True)
if len(asn) == 0:
    while(1):
        analyse()
        outmap()
        time.sleep(5)
else:

        while (1):
            analyse()
            recupresultasn(asn)
            time.sleep(5)

"""


#ASN Comcast : 7922
#données du 7 juin : 1465250400 => Panne au Kenya => https://atlas.ripe.net/api/v2/measurements/7000/results?start=1465250400&stop=1465336800&format=json
