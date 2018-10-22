package main
import (
  "golang.org/x/oauth2/google"
  "golang.org/x/oauth2"
  "golang.org/x/oauth2/jwt"
  "google.golang.org/api/compute/v1"
  "time"
  "fmt"
  "encoding/json"
  "os"
  "io/ioutil"
)

// A struct used for storing the necessary data from the service account input file.
// The file contains more information, but the only information needed for authentication
// are the client email and private key.
type Data struct {
  ClientEmail string `json:"client_email"`
  PrivateKey string `json:"private_key"`
}

// The Google Compute Engine interface
var service *compute.Service

// The project name in Google Cloud
const project = "eecs448-project-3"

// The zone in Google Cloud
const zone = "us-central1-c"

// Authenticate with Google Cloud using JWT and the existing service account.
// This gets the data from `key.json`.
func Init() {
  data := getAuthInfo()
  conf := &jwt.Config {
    Email: data.ClientEmail,
    PrivateKey: []byte(data.PrivateKey),
    Scopes: []string{
      "https://www.googleapis.com/auth/compute",
    },
    TokenURL: google.JWTTokenURL,
  }
  service, _ = compute.New(conf.Client(oauth2.NoContext))
}

// Gets the authentication information for Google Cloud from the proper file.
// The data is retrieved from `key.json`.
func getAuthInfo() Data {
  jsonFile, err := os.Open("key.json")

  if err != nil {
    fmt.Println(err)
    return Data{}
  }

  defer jsonFile.Close()

  bytes, _ := ioutil.ReadAll(jsonFile)
  var data Data
  json.Unmarshal(bytes, &data)
  return data
}

// Get the internal IP address of a given worker instance.
// The given id should be the name of the instance, such as "worker-1".
func GetIP(id string) (string, error) {
  res, err := service.Instances.Get(project, zone, id).Do()
  if err == nil {
    return res.NetworkInterfaces[0].NetworkIP, nil
  } else {
    return "", err
  }
}

// Wait until the given instance is in the expected state. This will timeout after 60 seconds.
// Id is the name of the instance to monitor (for example, "worker-1"), and expected is the
// state to wait for (for example, "TERMINATED").
func wait(id string, expected string) {
  status := ""
  start := TimeMillis()
  for status != expected && TimeMillis() - start < 60000 {
    res, _ := service.Instances.Get(project, zone, id).Do()
    status = res.Status
  }
}

// Reset a worker instance. This resets the VM to its initial state, stops the instance, and restarts it.
// The given Id is the name of the instance (for example, "worker-1").
// Returns an error if one occurs in the reset process.
func Reset(id string) error {
  fmt.Println("Resetting instance: " + id)
  _, err := service.Instances.Reset(project, zone, id).Do()
  time.Sleep(30 * time.Second);
  if err == nil {
    fmt.Println("\tStopping")
    _, err = service.Instances.Stop(project, zone, id).Do()
    wait(id, "TERMINATED")
    if err == nil {
      fmt.Println("\tStarting")
      _, err = service.Instances.Start(project, zone, id).Do()
      wait(id, "RUNNING")
      if err == nil {
        workers[id] = TimeMillis()
        fmt.Println("\tReset successful!")
      }
      return err
    }
  }
  return err
}
