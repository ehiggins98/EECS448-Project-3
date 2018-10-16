package main
import (
  "golang.org/x/oauth2/google"
  "golang.org/x/oauth2"
  "golang.org/x/oauth2/jwt"
  "google.golang.org/api/compute/v1"
  "time"
  "fmt"
)

var service *compute.Service
const project = "eecs448-project-3"
const zone = "us-central1-c"

func Init() {
  conf := &jwt.Config {
    Email: "router@eecs448-project-3.iam.gserviceaccount.com",
    PrivateKey: []byte("-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC2ns6EjA4VNIQW\nBcOFq8W8PDCGMD/fJs7Jvtwrw+38i6vCoadmIr8zc1xVf0Dw+eXl27z2VT2Dt/K9\nQy1XLm754EM+wwqibnA/CEDtjIchu4jPDLsOX1J0x+cmzKiuTDICzVdLtcZNlftb\nifIG1tntsDZriAlKi3UdhI4Nmo3xjM0UFr27HpSyWxRV2EH73mYVmaEqAF3y8z8r\niPgEU/ww5Xyz+j0ooex4kqmxe3CTE9lcpQVCW/kMO/fJKhG/4OlVLXoY5TxmJkg2\ndC7RzOXUNGOwlts1plYckqaQ9u2yiX1gM/ICDa6Gsu30FbC6YNKQUuJmXS/fWNZ1\nEWCxrKqTAgMBAAECggEADb6ZE3/JBY6MzG2FoDdj6/1pt4fFHuH4WVXMk1ytOj82\n37Cz/StrUY+CqQqpVBmy1GB78dxLg3DiS51VOcUMZDEdTol2cPA38X6JCHf1qbPI\nIbE3GOdSuOhcvN5VabzhXLWgttmJAcjigKq6tQoRn+KNzf0QmfQyDdUurdZujXnm\n7RiLBRo6i08y3zuCSmzpYclZqDR7jxL6MGwMWvNOgkvCjgCUK/liijNjQpW77Yvx\nd9wY2hIq9NWc9Hs0L6mdWGAfu3ZNVdxAQhdph+SdMzeUG2Dgx6idyfDYJgHJuFdz\nLSdEGHWMhEq9Z2diePdid7h/0fWp86UxK5Z/QrlNwQKBgQD/IFZa/+s2LQZ5cvNI\nhZwGNiRHwkrwtDoUkSMQq7d46m5zUJOrOUtDNWQtNJKjk1wDkH78qptaF8P965va\nTgCAyJG2SZkLKQzucox8mf/DvmHPNuNEe2aHaY0RKkZWpGruEJQ8el29AeW+Z6Ki\nlbswMr3X/jFHVmw8dncD2UoJwQKBgQC3Pue/DhK3UiTSMKXWCwxHLw/cRQ7JNcTA\npzSIImsu7m1xW46GR8zdPIrEhwfCRE+/YvfvTvXyinU8eZzRY50/oEfItbwZxWlg\nFFD4ZdRk98891FjHxZGoUNhFCmnqX/vdAD6q+4WlSPJcxcjhIIc/9NkvIPbyxOn2\n1I4Ep5HBUwKBgAY8gh/jVZqTay8Y0j2ZloDIXgarBy3vGeRaz+Keb/Oyt1R2ScXL\ntr1D1tkMCfGZrowfwhrnCLkhD5drZPnnIjgDrxwnnGgbbsd9YVXCZfAg/T8VdmS8\nJ3tz5xDeWa3QgxSirxzzWMs/+p+25NDYnCTHeMCI5Cd8Q1UPCEW90AOBAoGASxXl\nk+3KUX/BQrdYXJpuT4TDNPi/FEeJ9X8OEXI5BSQBiF+ByRgGo+i428qQrVOcccm1\n2kM6mEWPwFX8off1aSrd/yooh07S3OG2Q/JF05GPQ8CNGF6mTpfB5phbygPGikod\nY6Zons+DL+yDYWwYv2Yu0Bbr2ZJCZDe4ccPP/60CgYAa+FTYWfqYBLnRX3tI+vv3\nmnyPey/IzuMosg6kTKuDcMAFuq/wCuqBMaYIL3+H7hA3OzK9t/1reL7pxoROodMp\nW/dIFP+AWS0yzcJBTN++FLNkZjmw8Cq3mJC52lxZ21+GgyKf/5QUxVnyQEvGkK8I\nNgdQl0/g1jLmD5N9fhRPEw==\n-----END PRIVATE KEY-----\n"),
    Scopes: []string{
      "https://www.googleapis.com/auth/compute",
    },
    TokenURL: google.JWTTokenURL,
  }

  service, _ = compute.New(conf.Client(oauth2.NoContext))
}

func GetIP(id string) (string, error) {
  res, err := service.Instances.Get(project, zone, id).Do()
  if err == nil {
    return res.NetworkInterfaces[0].NetworkIP, nil;
  } else {
    return "", err;
  }
}

func wait(id string, expected string) {
  status := ""
  start := TimeMillis()
  for status != expected && TimeMillis() - start < 60000 {
    res, _ := service.Instances.Get(project, zone, id).Do()
    status = res.Status
  }
}

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
