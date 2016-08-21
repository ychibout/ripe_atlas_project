RIPE ATLAS Project
===================

Python 3 probe map creator and controller/country breakdown checker using the RIPE ATLAS REST API and the RIPE ATLAS Stream API.


Requirements
----------

This project uses some tools needed to be installed before.

This programm only works on Python3. If you havn't install it yet, you can download it at the official website : https://www.python.org/downloads/

First of all, you have to clone this Github Repository or just download the ZIP file : 

```
$ git clone https://github.com/ychibout/ripe_atlas_project.git
```
 
The first tool is RIPE ATLAS Cousteau, useful to communicate with the RIPE ATLAS API.

Install of RIPE ATLAS Cousteau:

```
$ apt-get install python3-ripe-atlas-cousteau
```

A node.js server is used to listen the stream of the RIPE ATLAS API.

Install of node.js

```
$ apt-get install nodejs
$ apt-get install nodejs-legacy
```

Finally, a MongoDB database, connected with the node.js server, will storage data sent from the stream API. We use the node.js API of MongoDB, named Mongoose, and the Python API, named PyMongo. 

Install of MongoDB:

```
$ apt-get install mongodb
```

Before installing Mongoose, the package manager of Node.js need to be installed :

```
$ apt-get install npm
```

Then, to install of Mongoose and the few others packages, you have to be in the '/ripe_atlas_project/main' folder:

```
$ npm install mongoose
$ npm install xmlhttprequest
```

Install of pymongo:

```
$ apt-get install python3-pymongo
```


Usage
----------

When you are in the Repository you've clone, just type this command :

```
$ python3 main/mapcreator.py
```

The program uses basically Chromium browser. You can change the browser to use by typing :

```
$ python3 main/mapcreator.py -b <browser_command>
```

You can also change the terminal used by program with :

```
$ python3 main/mapcreator.py -t <terminal_command>
```

You can define a filter by ASN to display on the map only probe with the given ASN :

```
$ python3 main/mapcreator.py --asn <as_number>
```

Or a filter by country code with --country option, or by controller with --controller option.

The usage is also explained by passing the option --help. 


Then, you will able to choose for example which ASN use as filter of the map marker displayer. If nothing is typed, the programm will display on the output map all probes of the RIPE Atlas Network.


Results
----------

When the programm begins to run, a new terminal will appear and run the node.js server. That server will "listen" the stream API of RIPE ATLAS. Each information about a probe state changing received by the server will be displayed on his terminal screen. 

At the same time, these informations are stored in a MongoDB Database. To check it, proceed like that :

```
$ mongo
MongoDB shell version: 2.4.9
connecting to: test
> use bdd1
switched to db bdd1
> db.probes.find()
```

Every 20 seconds (customizable), the python programm browse the database to check breakdowns first by countries, and in a second time, by probes owned by each controller. These results are displayed in the terminal screen, but can be saved in a file just by a redirection :

```
$ python3 main/mapcreator.py > out
```

Finally, the programm will create a map in the folder ./main (output.html) and places all markers related to probes in the database. This display could be filter by ASN, controller or country code. The freshing rate is 20 seconds (customizable).

Before recalling program, make sure that the database is empty. If it is not, these commands will fix the situation :

```
$ mongo
MongoDB shell version: 2.4.9
connecting to: test
> use bdd1
switched to db bdd1
> db.dropDatabase()
```

Additional details
----------

To learn more about this program, please consider comments in source code.

