RIPE ATLAS Project
===================

Python 3 probe map creator and controller/country breakdown checker using the RIPE ATLAS REST API and the RIPE ATLAS Stream API.


Requirements
----------

This project uses some tools needed to be installed before.
 
The first one is RIPE ATLAS Cousteau, useful to communicate with the RIPE ATLAS API.
With pip3 :

```
$ pip3 insall ripe.atlas.cousteau
```

A node.js server is used to listen the stream of the RIPE ATLAS API.

```
$ apt-get install nodejs
```

Finally, a MongoDB database, connected with the node.js server, will storage data sent from the stream API. We use the node.js API of MongoDB, named Mongoose, and the Python API, named PyMongo. 

Install of MongoDB:

```
$ apt-get install mongodb-org
```

Install of Mongoose:

```
$ npm install mongoose
```

Install of pymongo:

```
$ pip3 install pymongo
```


Of course, to use the programm, you have to clone this Github Repository 

```
$ git clone https://github.com/ychibout/ripe_atlas_project.git
```


Usage
----------

When you are in the Repository you've clone, just type this command :

```
$ python3 main/mapcreator.py
```

Then, you will able to choose which ASN use as filter of the map marker displayer. If nothing is typed, the programm will display on the output map all probes of the RIPE Atlas Network.


Results
----------

When the programm begins to run, a new terminal will appear and run the node.js server. That server will "listen" the stream API of RIPE ATLAS. Each information about a probe state changing received by the server will be displayed on his terminal screen. 

At the same time, these informations are stored in a MongoDB Database. To check it, proceed like that :

```
$ mongo
MongoDB shell version: 2.4.9
connecting to: test
> use bdd
switched to db bdd
> db.probes.find()
```

Every 20 seconds (customizable), the python programm browse the database to check breakdowns first by countries, and in a second time, by probes owned by each controller. These results are displayed in the terminal screen, but can be saved in a file just by a redirection :

```
$ python3 main/mapcreator.py > out
```

Finally, the programm will create a map in the folder ./main (output.html) and places all markers related to probes in the database. This display could be filter by ASN. The freshing rate is 20 seconds (customizable).


Additional details
----------

To learn more about this program, please consider comments in source code.

