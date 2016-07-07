from __future__ import print_function
import subprocess
from collections import namedtuple
from ripe.atlas.cousteau import AtlasRequest
from pymongo import MongoClient
import time
import sys
import datetime

client = MongoClient('mongodb://localhost')

class Map(object):
    def __init__(self):
        self.active = []    #Will contain all active probes of the database
        self.inactive = []  #Idem for the inactive probes
    def add_point(self, coordinates, status):
        if status == 1:
            self.active.append(coordinates)
        else:
            self.inactive.append(coordinates)
    def __str__(self):
        markersCode1 = "\n".join(   #A map marker of active probe
            [ """new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                map: map
                }});""".format(lat=x[0], lon=x[1]) for x in self.active
            ])
        markersCode2 = "\n".join(   #A map marker of inactive probe
            [ """new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                map: map
                }});""".format(lat=x[0], lon=x[1]) for x in self.inactive
            ])
        return """
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDN7jkdXxXCQrDfsuel6kciz8p9F6LzqBc"></script> <!-- please feed with your API Google Maps key -->
            <div id="map-canvas" style="height: 100%; width: 100%"></div>
            <script type="text/javascript">
                var map;
                function show_map() {{  <!-- Creating Map -->
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

def recupresultasn(asn) :   #Function called only if an ASN is given as filter
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


def listeprobe() :  #Store all probes of the RIPE ATLAS Network with their actual status
    db = client.bdd
    collection = db.probes
    i = 0
    count=0
    while i <= 18500:
        request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&offset=" + str(i)})
        result = namedtuple('Result', 'success response')
        (is_success, response) = request.get()

        for id in response["objects"]:
            #Searching for controller name using last status changing timestamp
            request = AtlasRequest(**{"url_path": "/api/v1/measurement/7000/result/?start=" + str(id["status_since"]) + "&stop=" + str(id["status_since"]) + "&prb_id=" + str(id["id"])})
            result = namedtuple('Result2', 'success response2')
            (is_success2, response2) = request.get()

            collection.insert_one(
                {
                    "id" : id["id"],
                    "status" : id["status"],
                    "timestamp" : id["last_connected"],
                    "latitude" : id["latitude"],
                    "longitude" : id["longitude"],
                    "controller" : "" if len(response2) == 0 else response2[0]["controller"],
                    "asn" : id["asn_v4"],
                    "country_code" : id["country_code"]
                }
            )

            count+=1

            print(str((count/18630)*100) + " %")

        i+=500

def listeprobeasn(asn): #Store probes attached to the AS with the given ASN
    db = client.bdd
    collection = db.probes
    request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&asn=" + str(asn)})
    result = namedtuple('Result', 'success response')
    (is_success, response) = request.get()
    count=0
    for id in response["objects"]:

        request = AtlasRequest(**{"url_path": "/api/v1/measurement/7000/result/?start=" + str(id["status_since"]) + "&stop=" + str(id["status_since"]) + "&prb_id=" + str(id["id"])})
        result = namedtuple('Result2', 'success response2')
        (is_success2, response2) = request.get()

        collection.insert_one(
            {
                "id" : id["id"],
                "status" : id["status"],
                "timestamp" : id["last_connected"],
                "latitude" : id["latitude"],
                "longitude" : id["longitude"],
                "controller" : "" if len(response2) == 0 else response2[0]["controller"],
                "asn" : id["asn_v4"],
                "country_code" : id["country_code"]
            }
        )

        count+=1

        print(str((count/response["meta"]["total_count"])*100) + " %")

def outmap() :  #creation of the map using the Google Maps API
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

def analyse():  #Check country/controller breakdown
        db = client.bdd
        collection = db.probes
        print(datetime.datetime.fromtimestamp(time.time()))
        print("Last status changing timestamp :  " + datetime.datetime.fromtimestamp(db.probes.find_one({"$query":{},"$orderby":{"timestamp":-1}})["timestamp"]).strftime('%c') + "\n")
        print("Country Breakdown : ")
        for res in collection.distinct("country_code"):
            if collection.count({"country_code" : res}) >= 3 and (collection.count({"country_code" : res, "status" : "disconnect"}) / collection.count({"country_code" : res})) > 0.9 :
                print("\t" + res + " down : " + str(collection.count({"country_code" : res, "status" : "disconnect"})) + " probes of " + str(collection.count({"country_code" : res})) + " disconnected")
        print("Controller breakdown : ")
        for res in collection.distinct("controller"):
            if collection.count({"controller" : res}) >= 3 and (collection.count({"controller" : res, "status" : "disconnect"}) / collection.count({"controller" : res})) > 0.9 :
                print("\tcontroller " + res + " down : " + str(collection.count({"controller" : res, "status" : "disconnect"})) + " probes of " + str(collection.count({"controller" : res})) + " disconnected")
        print("\n")

if len(sys.argv) != 1 and sys.argv[1] == "--help":
    print("\nUsage : python3 mapcreator.py [-t] [TERMINAL_NAME] [-b] [BROWSER_NAME]\n\n\t-t : define terminal used by the program\n\t-b : Define browser used by the program")
else:
    print("Please choose an ASN as filter : ")
    asn = input(" >> ")

    varpwd = subprocess.check_output("pwd")
    newpwd = str(varpwd).replace("b'","")
    newpwd2 = str(newpwd).replace("n'","")
    newpwd3 = str(newpwd2).replace("\\","")


    if len(str(asn)) == 0:   #No filter case
        print("\n\t\tPlease wait during the storage of all probes data...\n")
        listeprobe()

        if len(sys.argv) == 3:
            if str(sys.argv[1]) == "-t":
                subprocess.Popen(str(sys.argv[2]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)
            elif str(sys.argv[1]) == "-b":
                subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[2]) + " " + newpwd3 + "/socketapi.html", shell=True)
            else:
                print("Error during passing of arguments")
        elif len(sys.argv) == 5:
            if str(sys.argv[1]) == "-t":
                subprocess.Popen(str(sys.argv[2]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
            elif str(sys.argv[1]) == "-b":
                subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[2]) + " " + newpwd3 + "/socketapi.html", shell=True)
            else:
                print("Error during passing of arguments")
        else:
            subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)

        while(1):
            analyse()
            outmap()
            time.sleep(20)

    else:   #ASN filter case
        print("\n\t\tPlease wait during the storage of all probes data...\n")
        listeprobeasn(asn)

        if len(sys.argv) == 3:
            if str(sys.argv[1]) == "-t":
                subprocess.Popen(str(sys.argv[2]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)
            elif str(sys.argv[1]) == "-b":
                subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[2]) + " " + newpwd3 + "/socketapi.html", shell=True)
            else:
                print("Error during passing of arguments")
        elif len(sys.argv) == 5:
            if str(sys.argv[1]) == "-t":
                subprocess.Popen(str(sys.argv[2]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
            elif str(sys.argv[1]) == "-b":
                subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
                subprocess.Popen(str(sys.argv[2]) + " " + newpwd3 + "/socketapi.html", shell=True)
            else:
                print("Error during passing of arguments")
        else:
            subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)

        while(1):
            analyse()
            recupresultasn(asn)
            time.sleep(20)
