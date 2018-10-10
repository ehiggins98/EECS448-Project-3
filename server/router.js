
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

app.post('/', function(req, res) {
  var options = {
    method: 'POST',
    uri: worker,
    body: req.body,
    json: true // Automatically stringifies the body to JSON
  };

  request(options).then(r => {
    res.send(r);
  });
});
