
function GPS_for_Tracking() {

}

function getGPS(resultFunction) {
    navigator.geolocation.watchPosition(resultFunction, GPSResultError);
}

function GPSResultError(error) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      window.alert("User denied the request for Geolocation.")
      break;
    case error.POSITION_UNAVAILABLE:
      window.alert("Location information is unavailable.")
      break;
    case error.TIMEOUT:
      window.alert("The request to get user location timed out.")
      break;
    case error.UNKNOWN_ERROR:
      window.alert("An unknown error!")
      break;
  }
}