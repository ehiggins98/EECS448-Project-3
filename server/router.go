package main
import (
  "net/http"
  "time"
  "errors"
  "io/ioutil"
  "bytes"
  "fmt"
)

var workers map[string]int64
var postClient http.Client

///Gets the current system time in milliseconds.
func TimeMillis() int64 {
  return time.Now().UnixNano() / int64(time.Millisecond);
}

///Gets the IP address of an available execution server from workers.
func getExecutor() (string, error) {
  for k := range workers {
    delete(workers, k)
    return k, nil
  }
  return "", errors.New("Length of workers is 0")
}

///Builds a request with properties
/// URL: http://{server}
/// Method: POST
/// Headers: {Content-Type: application/json}
func makeRequest(server string, body string) *http.Request {
  url := "http://" + server
  req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(body)))
  req.Header.Set("Content-Type", "application/json")
  return req;
}

///Accepts a request from the user and forwards it to the appropriate worker.
///If the server doesn't respond, it will be reset and rebooted asychronously.
func forward(w http.ResponseWriter, r *http.Request) {
  body, _ := ioutil.ReadAll(r.Body)

  for true {
    if len(workers) > 0 {
      executor, _ := getExecutor()
      ip, _ := GetIP(executor)
      resp, err := postClient.Do(makeRequest(ip, string(body)))

      if err == nil {
        body, _ = ioutil.ReadAll(resp.Body);
        w.WriteHeader(200)
        w.Write(body)
        workers[executor] = TimeMillis()
      } else {
        fmt.Println(err)
        w.WriteHeader(500)
        go Reset(executor)
      }

      break
    }
  }
}

///Main function. Initializes the server and the list of available workers.
func main() {
  workers = map[string]int64{"worker-1": TimeMillis(), "worker-2": TimeMillis()}
  timeout := time.Duration(8 * time.Second)
  postClient = http.Client {
    Timeout: timeout,
  }
  Init()
  http.HandleFunc("/", forward)
  err := http.ListenAndServe(":8080", nil)
  if err != nil {
    panic(err)
  }
}
