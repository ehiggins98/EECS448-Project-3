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
var executing = false;

http.createServer(app).listen(HTTP_PORT,function() {
  console.log('Listening HTTP on port ' + HTTP_PORT);
});

app.get('/', function(req, res) {
  executing ? res.sendStatus(404) : res.sendStatus(200);
});

app.post('/', function(req, res) {
  executing = true;
  let params = req.body["params"];
  let code = req.body["code"];
  res.send(executor(params, code));
  executing = false;
});
