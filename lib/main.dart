import 'package:flutter/material.dart';
import 'dart:async';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';

void main() => runApp(new MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return new MaterialApp(
      title: 'Flutter Demo',
      theme: new ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or press Run > Flutter Hot Reload in IntelliJ). Notice that the
        // counter didn't reset back to zero; the application is not restarted.
        primarySwatch: Colors.blue,
      ),
      home: new MyHomePage(title: 'Code Compiler'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  _MyHomePageState createState() => new _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  var _image;

  Future takePic() async {
    var image = await ImagePicker.pickImage(source: ImageSource.camera);

    setState(() {
      _image = image;
    });

    Dio dio = new Dio();
    FormData formdata = new FormData.from({
      "file": new UploadFileInfo(_image, _image.path)
    });
    var response = await dio.post('http://35.208.187.194', data: formdata, options: Options(
        method: 'POST',
        responseType: ResponseType.PLAIN // or ResponseType.JSON
    ))
        .then((response) => print(response))
        .catchError((error) => print(error));
  }

  Future getPic() async {
    var image = await ImagePicker.pickImage(source: ImageSource.gallery);
    setState(() {
      _image = image;
    });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return new Scaffold(
      appBar: new AppBar(
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: new Text(widget.title),
        centerTitle: true,
//        actions: <Widget>[
//          FlatButton(child: Icon(Icons.photo, color: Colors.white), splashColor: Colors.white, highlightColor: Colors.white, onPressed: getPic)
//        ],
      ),
      body: new Center(

        child: _image == null
            ? Text('No image selected.')
            : Image.file(_image),
      ),

      floatingActionButton: new FloatingActionButton(
        onPressed: takePic,
        tooltip: 'Pick Image',
        child: new Icon(Icons.add_a_photo),
      ),
      // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
