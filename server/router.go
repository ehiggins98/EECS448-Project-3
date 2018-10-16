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

func TimeMillis() int64 {
  return time.Now().UnixNano() / int64(time.Millisecond);
}

func getExecutor() (string, error) {
  for k := range workers {
    delete(workers, k)
    return k, nil
  }
  return "", errors.New("Length of workers is 0")
}

func makeRequest(server string, body string) *http.Request {
  url := "http://" + server
  req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(body)))
  req.Header.Set("Content-Type", "application/json")
  return req;
}

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

func main() {
  workers = map[string]int64{"worker-1": TimeMillis(), "worker-2": TimeMillis()}
  timeout := time.Duration(8 * time.Second)
  postClient = http.Client {
    Timeout: timeout,
  }
  Init()
  http.HandleFunc("/", forward)
  err := http.ListenAndServe(":3000", nil)
  if err != nil {
    panic(err)
  }
}
