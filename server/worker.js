var express = require('express');
var fs = require('fs');
var path = require('path');
var http = require('http');
var https = require('https');
var forward = require('http-forward');
var app = express();

var HTTP_PORT = 80;

http.createServer(app).listen(HTTP_PORT,function() {
  console.log('Listening HTTP on port ' + HTTP_PORT);
});


app.post('/', function(req, res) {
  console.log(req.body);
  res.sendStatus(200);
  res.send(req.body);
});
