var express = require('express');
var fs = require('fs');
var path = require('path');
var http = require('http');
var https = require('https');
var forward = require('http-forward');

var executor = require('./executor');

var app = express();
app.use(express.json());

var HTTP_PORT = 80;

http.createServer(app).listen(HTTP_PORT,function() {
  console.log('Listening HTTP on port ' + HTTP_PORT);
});

app.post('/', function(req, res) {
  let params = req.body["params"];
  let code = req.body["code"];
  res.send(executor(params, code));
});
