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

func timeMillis() int64 {
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
      resp, err := postClient.Do(makeRequest(executor, string(body)))

      if err == nil {
        body, _ = ioutil.ReadAll(resp.Body);
        fmt.Println(string(body))
        w.WriteHeader(200)
        w.Write(body)
      } else {
        w.WriteHeader(500)
      }

      workers[executor] = timeMillis()
      break
    }
  }
}

func main() {
  workers = map[string]int64{"localhost:3001": timeMillis(), "localhost:3002": timeMillis()}
  timeout := time.Duration(15 * time.Second)
  postClient = http.Client {
    Timeout: timeout,
  }

  http.HandleFunc("/", forward)
  err := http.ListenAndServe(":3000", nil)
  if err != nil {
    panic(err)
  }
}
