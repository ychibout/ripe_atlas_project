var mongoose = require('mongoose');
var url = require('url');
var http = require('http');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;


mongoose.connect('mongodb://localhost/bdd', function(err) {
        if (err) {throw err;}
});

var ProbeSchema = new mongoose.Schema({
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

function Get(Url){
        var Httpreq = new XMLHttpRequest();
        Httpreq.open("GET",Url,false);
        Httpreq.send(null);
        return Httpreq.responseText;
}


http.createServer(function(request, response) {
        response.writeHead(200, {"Content-Type":"text/plain"});
        var params = url.parse(request.url, true).query;

        var ProbeModel = mongoose.model('probe', ProbeSchema);

        var pid = params.id;
        var pstatus = params.status;
        var ptimestamp = params.timestamp;
        var pcontroller = params.controller;
        var pasn = params.asn;

        ProbeModel.count({"id" : pid}, function (err, nb) {
                if (nb > 0) {
                        ProbeModel.findOne({"id" : pid}, function (err, probe) {
                                probe.status = pstatus;
                                probe.timestamp = ptimestamp;
                                probe.controller = pcontroller;
                                probe.save();
                                console.log("id probe : " + pid);
                                console.log("status : " + pstatus);
                                console.log("timestamp : " + ptimestamp);
                                console.log("asn : " + pasn);
                                console.log("Mise à jour de la probe\n");
                        });
                }
                else {
                        var requrl = 'https://atlas.ripe.net/api/v1/probe/?format=json&id__in=' + pid;

                        var longlat = JSON.parse(Get(requrl));

                        var plong = longlat.objects[0].longitude;
                        var plat = longlat.objects[0].latitude;
                        var pcc = longlat.objects[0].country_code;

                        new ProbeModel({
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
                                console.log("Probe ajoutée à la base de données\n");
                        });
                }
        });
}).listen(10001);


/*use blog
switched to db blog
> show collections
commentaires
system.indexes
> db.commentaires.find()

Pour supprimer :
use [database];
db.dropDatabase();
*/
