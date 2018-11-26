import 'package:flutter/material.dart';
import 'dart:async';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'dart:convert';

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


class TestPage extends StatelessWidget {
  final String text;
  TestPage({Key key, @required this.text});

  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Text("Unit Tests"),
        ),
        body: Padding(padding: EdgeInsets.all(16.0), child: SingleChildScrollView(child: Text(this.text))));
  }
}

class CodeOutput extends StatelessWidget {
  final String text;
  CodeOutput({Key key, @required this.text});

  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Text("Code Output"),
        ),
        body: Padding(padding: EdgeInsets.all(16.0), child: SingleChildScrollView(child: Text(this.text))));
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
  var _text = "Take a Picture";
  var _showEditor = false;
  final TextEditingController _controller = new TextEditingController(
    text: 'This is where the code will be'
  );
  final FocusNode _focusNode = new FocusNode();

  Future takePic() async {
    var image = await ImagePicker.pickImage(source: ImageSource.camera);
    var text;


    setState(() {
      _image = image;
      _text = text;
    });

    showEditor();


//    print('showing snack bar');

// Find the Scaffold in the Widget tree and use it to show a SnackBar
  }

  showEditor() async{
    Dio dio = new Dio();
    FormData formdata = new FormData.from({
       "file": new UploadFileInfo(_image, _image.path)
     });
    setState(() {
          _showEditor = true;
        });
    
    // Some code to get back code from the picture
    var response = await dio.post('http://35.208.187.194:5000', data: formdata, options: Options(
         method: 'POST',
         responseType: ResponseType.PLAIN // or ResponseType.JSON
     ))
         .then((response) => setState(() {
           _image = null;
           this._showEditor = true;
           _controller.text = response.toString();
           print('controller text is ${_controller.text}');

           }))
         .catchError((error) => print(error));

  }

  submitCode() async{
    Dio dio = new Dio();
    /*FormData formdata = new FormData.from({
       "file": new UploadFileInfo(_image, _image.path)
    });*/
    print("hello");
    var data = json.encode({
      "params": [],
      "code": _controller.text.toString()
    });
    print(data);
    var response = await dio.post('http://35.193.209.164', data: data, options: Options(
         method: 'POST',
         responseType: ResponseType.JSON // or ResponseType.JSON
     ))
         .then((response) => setState(() {
        
           _image = null;
          int length = response.data.length - 1;
          Navigator.push(context,
          MaterialPageRoute(builder: (context) => TestPage(text: response.data.substring(1, length))));
          }))
         .catchError((error) => print(error));
  }
 runTests() async {
    Dio dio = new Dio();
    
    Response<String> response = await dio.get("http://35.208.187.194",options: Options(
         method: 'GET',
         responseType: ResponseType.JSON // or ResponseType.JSON
     ));

    Navigator.push(context,
        MaterialPageRoute(builder: (context) => TestPage(text: response.data)));
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
        actions: <Widget>[
          FlatButton(child: Icon(Icons.photo, color: Colors.white), splashColor: Colors.white, highlightColor: Colors.white, onPressed: getPic),
          FlatButton(child: Icon(Icons.file_upload, color: Colors.white), splashColor: Colors.white, highlightColor: Colors.white, onPressed: submitCode),
     
          FlatButton(onPressed: (){
            //showEditor();
            runTests();
            //submitCode("hello");
          }, child: Text('Unit Test', style: TextStyle(color: Colors.white),),)
        ],
        centerTitle: true

      ),
      body: new Center(

        child: _showEditor == true ? TextFormField(
          onFieldSubmitted: (String response){
            submitCode();
          },
          controller: _controller,
          focusNode: _focusNode,
          decoration: InputDecoration(
            contentPadding: EdgeInsets.all(8.0),
            border: InputBorder.none
          )
        ) : SizedBox(
          child: Text(_text),
        )
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
