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
            [ """var info{name} = new google.maps.InfoWindow({{
                    content:'<p><b>ID</b> : {id} </br> <b>ASN</b> : {asn} </br> <b>Country Code</b> : {country_code}<br\></p>'
                }});

            var marker{name} = new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                map: map,
                title: {id}
            }});

            marker{name}.addListener('click', function() {{
                info{name}.open(map, marker{name});
            }});""".format(lat=x[0], lon=x[1], name=self.active.index(x), id=x[2], asn=x[3], country_code=x[4]) for x in self.active
            ])
        markersCode2 = "\n".join(   #A map marker of inactive probe
            [ """var info{name} = new google.maps.InfoWindow({{
                    content:'<p><b>ID</b> : {id} </br> <b>ASN</b> : {asn} </br> <b>Country Code</b> : {country_code}<br\></p>'
                }});

            var marker{name} = new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                map: map,
                title: {id}
            }});

            marker{name}.addListener('click', function() {{
                info{name}.open(map, marker{name});
            }});""".format(lat=x[0], lon=x[1], name=self.inactive.index(x) + len(self.active), id=x[2], asn=x[3], country_code=x[4]) for x in self.inactive
            ])
        panel1 = "\n".join([
            """<tr>
                    <td class="id">{id}</td>
                    <td class="asn">{asn}</td>
                    <td class="cc">{country_code}
                </tr>""".format(id=x[2], asn=x[3], country_code=x[4]) for x in self.active])
        panel2 = "\n".join([
            """<tr>
                    <td class="id">{id}</td>
                    <td class="asn">{asn}</td>
                    <td class="cc">{country_code}
                </tr>""".format(id=x[2], asn=x[3], country_code=x[4]) for x in self.inactive])
        return """
                <meta http-equiv="refresh" content="20">
                <style>
                    button.accordion {{
                        background-color: #eee;
                        color: #444;
                        cursor: pointer;
                        padding: 18px;
                        width: 50%;
                        border: none;
                        text-align: left;
                        outline: none;
                        float: right;
                        font-size: 15px;
                        transition: 0.4s;
                    }}

                    button.accordion.active, button.accordion:hover {{
                        background-color: #ddd;
                    }}

                    button.accordion:after {{
                        content: '+';
                        font-size: 13px;
                        color: #777;
                        float: right;
                        margin-left: 5px;
                    }}

                    button.accordion.active:after {{
                        content: "-";
                        float: right;
                    }}

                    div.panel1 {{
                        padding: 0 18px;
                        background-color: white;
                        max-height: 0;
                        float: right;
                        overflow: hidden;
                        transition: 0.6s ease-in-out;
                        opacity: 0;
                        padding-left:50%;
                    }}

                    div.panel1.show {{
                        opacity: 1;
                        max-height: 100000px;
                        font-family : "arial";
                        width:48%;
                    }}

                    div.panel2 {{
                        padding: 0 18px;
                        background-color: white;
                        max-height: 0;
                        overflow: hidden;
                        float: right;
                        transition: 0.6s ease-in-out;
                        opacity: 0;
                        padding-left:51%;
                    }}

                    div.panel2.show {{
                        opacity: 1;
                        max-height: 100000px;
                        font-family : "arial";
                        width:48%;
                    }}

                    table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}

                    th, td {{
                        text-align:left;
                        padding:8px;
                    }}

                    tr:nth-child(even){{
                    background-color: #f2f2f2
                    }}

                    input {{
                        width: 130px;
                        box-sizing: border-box;
                        border: 2px solid #ccc;
                        border-radius: 4px;
                        font-size: 16px;
                        background-color: white;
                        background-position: 10px 10px;
                        background-repeat: no-repeat;
                        padding: 5px 20px 5px 40px;
                        -webkit-transition: width 0.4s ease-in-out;
                        transition: width 0.4s ease-in-out;
                    }}

                    input:focus {{
                        width: 100%;
                    }}

                    button.sort {{
                        background-color: #e7e7e7;
                        color: black;
                        border: none;
                        padding: 10px 16px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                    }}
                </style>

                <button class="accordion">Connected Probes : {coprobes}</button>
                <div id="panel1" class="panel1">
                    <br>
                    <input class="search" placeholder="Search" />
                    <br>
                    <br>
                    <button class="sort" data-sort="id">Sort by ID</button>
                    <button class="sort" data-sort="asn">Sort by ASN</button>
                    <button class="sort" data-sort="cc">Sort by Country Code</button>
                    <br>
                    <br>
                    <table>
                        <thead>
                            <th class="sort" data-sort="id">ID</th>
                            <th class="sort" data-sort="asn">ASN</th>
                            <th class="sort" data-sort="cc">Country Code</th>
                        </thead>
                        <tbody class="list">
                            {panel1}
                        </tbody>
                    </table>
                </div>

                <script src="https://cdnjs.cloudflare.com/ajax/libs/list.js/1.2.0/list.min.js"></script>
                <script type="text/javascript">
                    var options = {{
                        valueNames: [ 'id', 'asn', 'cc' ]
                    }};
                    var probeList = new List('panel1', options);
                </script>

                <button class="accordion">Disconnected Probes : {discoprobes}</button>
                <div id="panel2" class="panel2">
                    <br>
                    <input class="search" placeholder="Search" />
                    <br>
                    <br>
                    <button class="sort" data-sort="id">Sort by ID</button>
                    <button class="sort" data-sort="asn">Sort by ASN</button>
                    <button class="sort" data-sort="cc">Sort by Country Code</button>
                    <br>
                    <br>
                    <table>
                        <thead>
                            <th class="sort" data-sort="id">ID</th>
                            <th class="sort" data-sort="asn">ASN</th>
                            <th class="sort" data-sort="cc">Country Code</th>
                        </thead>
                        <tbody class="list">
                            {panel2}
                        </tbody>
                    </table>
                </div>

                <script type="text/javascript">
                    var options = {{
                        valueNames: [ 'id', 'asn', 'cc' ]
                    }};
                    var probeList = new List('panel2', options);
                </script>

                <script>
                    var acc = document.getElementsByClassName("accordion");
                    var i;

                    for (i = 0; i < acc.length; i++) {{
                        acc[i].onclick = function(){{
                            this.classList.toggle("active");
                            this.nextElementSibling.classList.toggle("show");
                      }}
                    }}
                </script>

                <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDN7jkdXxXCQrDfsuel6kciz8p9F6LzqBc"></script>
                <div id="map-canvas" style="height: 100%; width: 50%; float:left; position: absolute"></div>
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

        """.format(markersCode1=markersCode1, markersCode2=markersCode2, coprobes=len(self.active), discoprobes=len(self.inactive), panel1=panel1, panel2=panel2)

def recupresultasn(asn) :   #Function called only if an ASN is given as filter
    map = Map()
    db = client.bdd1
    collection = db.probes

    for elem in collection.find():
        if str(elem["asn"]) == asn:
            if elem["status"] == 1 or elem["status"] == "connect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 1)
            if elem["status"] == 2 or elem["status"] == "disconnect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)



def recupresultcountry(country) :   #Function called only if an ASN is given as filter
    map = Map()
    db = client.bdd1
    collection = db.probes

    for elem in collection.find():
        if str(elem["country_code"]) == country:
            if elem["status"] == 1 or elem["status"] == "connect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 1)
            if elem["status"] == 2 or elem["status"] == "disconnect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)


def recupresultcontroller(controller) :   #Function called only if an ASN is given as filter
    map = Map()
    db = client.bdd1
    collection = db.probes

    for elem in collection.find():
        if str(elem["controller"]) == controller:
            if elem["status"] == 1 or elem["status"] == "connect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 1)
            if elem["status"] == 2 or elem["status"] == "disconnect":
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)



def listeprobe() :  #Store all probes of the RIPE ATLAS Network with their actual status
    db = client.bdd1
    collection = db.probes
    i = 0
    count=0
    while i <= 18500:
        request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&offset=" + str(i)})
        result = namedtuple('Result', 'success response')
        (is_success, response) = request.get()

        for id in response["objects"]:
            if id["status"] == 1 or id["status"] == 2:
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

        i+=500

def listeprobeasn(asn): #Store probes attached to the AS with the given ASN
    db = client.bdd1
    collection = db.probes
    request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&asn=" + str(asn)})
    result = namedtuple('Result', 'success response')
    (is_success, response) = request.get()
    count=0

    for id in response["objects"]:
        if id["status"] == 1 or id["status"] == 2:
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


def listeprobecountry(country): #Store probes attached to the chosen country
    db = client.bdd1
    collection = db.probes
    request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&country_code=" + str(country)})
    result = namedtuple('Result', 'success response')
    (is_success, response) = request.get()
    count=0

    for id in response["objects"]:
        if id["status"] == 1 or id["status"] == 2:
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


def listeprobecontroller(controller): #Store probes attached to the given controller
    db = client.bdd1
    collection = db.probes
    i = 0
    count=0
    while i <= 18500:
        request = AtlasRequest(**{"url_path": "/api/v1/probe/?limit=500&offset=" + str(i)})
        result = namedtuple('Result', 'success response')
        (is_success, response) = request.get()

        for id in response["objects"]:
            if id["status"] == 1 or id["status"] == 2:
                request = AtlasRequest(**{"url_path": "/api/v1/measurement/7000/result/?start=" + str(id["status_since"]) + "&stop=" + str(id["status_since"]) + "&prb_id=" + str(id["id"])})
                result = namedtuple('Result2', 'success response2')
                (is_success2, response2) = request.get()

                if len(response2) > 0 and response2[0]["controller"] == controller:
                    collection.insert_one(
                        {
                            "id" : id["id"],
                            "status" : id["status"],
                            "timestamp" : id["last_connected"],
                            "latitude" : id["latitude"],
                            "longitude" : id["longitude"],
                            "controller" : response2[0]["controller"],
                            "asn" : id["asn_v4"],
                            "country_code" : id["country_code"]
                        }
                    )


def outmap() :  #creation of the map using the Google Maps API
    map = Map()
    db = client.bdd1
    collection = db.probes

    for elem in collection.find():
            if elem["status"] == "connect" or elem["status"] == 1:
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 1)
            if elem["status"] == "disconnect" or elem["status"] == 2:
                map.add_point((elem["latitude"], elem["longitude"], elem["id"], elem["asn"], elem["country_code"]), 2)

    with open("output.html", "w") as out:
        print(map, file=out)

def analyse():  #Check country/controller breakdown
        db = client.bdd1
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
    print("\nUsage : python3 mapcreator.py [OPTIONS][OPTIONS_ARGS]\n\n\t-t : define terminal used by the program, need the terminal name in argument\n\t-b : Define browser used by the program, need the browser name in argument\n\t--asn : Filter probes by ASN, need a asn in argument\n\t--country : Filter probes by country, need a country code in argument\n\t--controller : Filter probes by controller attachment, need a controller name in argument")


elif len(sys.argv) != 1 and sys.argv[1] == "--asn":
    asn = sys.argv[2]

    varpwd = subprocess.check_output("pwd")
    newpwd = str(varpwd).replace("b'","")
    newpwd2 = str(newpwd).replace("n'","")
    newpwd3 = str(newpwd2).replace("\\","")


    print("\n\t\tPlease wait during the storage of all probes data...\n")
    listeprobeasn(asn)

    if len(sys.argv) == 5:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[3]) == "-b":
            subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    elif len(sys.argv) == 7:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[6]) + " " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[1]) == "-b":
            subprocess.Popen(str(sys.argv[6]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    else:
        subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
        subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)

    while(1):
        analyse()
        recupresultasn(asn)
        time.sleep(20)

elif len(sys.argv) != 1 and sys.argv[1] == "--country" :
    country = sys.argv[2]

    varpwd = subprocess.check_output("pwd")
    newpwd = str(varpwd).replace("b'","")
    newpwd2 = str(newpwd).replace("n'","")
    newpwd3 = str(newpwd2).replace("\\","")


    print("\n\t\tPlease wait during the storage of all probes data...\n")
    listeprobecountry(country)

    if len(sys.argv) == 5:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[3]) == "-b":
            subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    elif len(sys.argv) == 7:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[6]) + " " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[1]) == "-b":
            subprocess.Popen(str(sys.argv[6]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    else:
        subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
        subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)

    while(1):
        analyse()
        recupresultcountry(country)
        time.sleep(20)


elif len(sys.argv) != 1 and sys.argv[1] == "--controller" :
    controller = sys.argv[2]

    varpwd = subprocess.check_output("pwd")
    newpwd = str(varpwd).replace("b'","")
    newpwd2 = str(newpwd).replace("n'","")
    newpwd3 = str(newpwd2).replace("\\","")


    print("\n\t\tPlease wait during the storage of all probes data...\n")
    listeprobecontroller(controller)

    if len(sys.argv) == 5:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[3]) == "-b":
            subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    elif len(sys.argv) == 7:
        if str(sys.argv[3]) == "-t":
            subprocess.Popen(str(sys.argv[4]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[6]) + " " + newpwd3 + "/socketapi.html", shell=True)
        elif str(sys.argv[1]) == "-b":
            subprocess.Popen(str(sys.argv[6]) + " -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
            subprocess.Popen(str(sys.argv[4]) + " " + newpwd3 + "/socketapi.html", shell=True)
        else:
            print("Error during passing of arguments")
    else:
        subprocess.Popen("x-terminal-emulator -e 'node " + newpwd3 + "/mongooseserver.js'", shell=True)
        subprocess.Popen("chromium-browser --new-window " + newpwd3 + "/socketapi.html", shell=True)

    while(1):
        analyse()
        recupresultcontroller(controller)
        time.sleep(20)


else:
        varpwd = subprocess.check_output("pwd")
        newpwd = str(varpwd).replace("b'","")
        newpwd2 = str(newpwd).replace("n'","")
        newpwd3 = str(newpwd2).replace("\\","")

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
