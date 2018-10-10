var express = require('express');
var fs = require('fs');
var path = require('path');
var http = require('http');
var https = require('https');
var forward = require('http-forward');
var app = express();

var HTTP_PORT = 3000;

// Create an HTTP service
http.createServer(app).listen(HTTP_PORT,function() {
  console.log('Listening HTTP on port ' + HTTP_PORT);
});


//endpoint for tracking
app.get('/', function(req, res) {
  req.forward = { target: '10.128.0.3' };
  forward(req, res);
});

function processRequest(req){
    console.log("request processed");
}
