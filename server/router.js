var express = require('express');
var fs = require('fs');
var path = require('path');
var http = require('http');
var https = require('https');
var request = require('request-promise');

var app = express();
app.use(express.json());

var HTTP_PORT = 80;
const worker = "http://10.128.0.4";

http.createServer(app).listen(HTTP_PORT,function() {
  console.log('Listening HTTP on port ' + HTTP_PORT);
});

app.get('/', function(req, res) {
  request(worker).then(r => {
    res.send(r);
  });
});
