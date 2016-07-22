var mongoose = require('mongoose');
var url = require('url');
var http = require('http');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;


mongoose.connect('mongodb://localhost/bdd1', function(err) {     //connection to the MongoDB database with Mongoose client
        if (err) {throw err;}
});

var ProbeSchema = new mongoose.Schema({ //Creating the type of data which will be stored in database
        id : {type : Number},
        status : {type : String},
        timestamp : {type : Number},
        latitude : {type : Number},
        longitude : {type : Number},
        controller : {type : String},
        asn : {type : String},
        country_code : {type : String}
});

var map;

function Get(Url){      //Create a HTTP request to get data inside the URL created before
        var Httpreq = new XMLHttpRequest();
        Httpreq.open("GET",Url,false);
        Httpreq.send(null);
        return Httpreq.responseText;
}


http.createServer(function(request, response) {
        response.writeHead(200, {"Content-Type":"text/plain"});
        var params = url.parse(request.url, true).query;        //parse the url

        var ProbeModel = mongoose.model('probe', ProbeSchema);

        //data from the url :
        var pid = params.id;
        var pstatus = params.status;
        var ptimestamp = params.timestamp;
        var pcontroller = params.controller;
        var pasn = params.asn;

        ProbeModel.count({"id" : pid}, function (err, nb) {
                if (nb > 0) {   //if the probe exists in the database => modifications of the info about it
                        ProbeModel.findOne({"id" : pid}, function (err, probe) {
                                probe.status = pstatus;
                                probe.timestamp = ptimestamp;
                                probe.controller = pcontroller;
                                probe.asn = pasn;
                                probe.save();
                                console.log("id probe : " + pid);
                                console.log("status : " + pstatus);
                                console.log("timestamp : " + ptimestamp);
                                console.log("asn : " + pasn);
                                console.log("Updating probe informations\n");
                        });
                }
                else {  //if the probe doesn't exist in the db
                        var requrl = 'https://atlas.ripe.net/api/v1/probe/?format=json&id__in=' + pid;
                        //We have to get back the longitude, latitude and country from the REST API
                        var longlat = JSON.parse(Get(requrl));

                        var plong = longlat.objects[0].longitude;
                        var plat = longlat.objects[0].latitude;
                        var pcc = longlat.objects[0].country_code;

                        new ProbeModel({        //Creating a new entry
                                id : pid,
                                status : pstatus,
                                timestamp : ptimestamp,
                                latitude : plat,
                                longitude : plong,
                                controller : pcontroller,
                                asn : pasn,
                                country_code : pcc
                        }).save(function(err) {
                                if (err) {throw err;}
                                console.log("id probe : " + pid);
                                console.log("status : " + pstatus);
                                console.log("timestamp : " + ptimestamp);
                                console.log("longitude : " + plong);
                                console.log("latitude : " + plat);
                                console.log("controller : " + pcontroller);
                                console.log("asn : " + pasn);
                                console.log("country_code : " + pcc);
                                console.log("Probe added to the Database\n");
                        });
                }
        });
}).listen(10001);
