document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
//var server_addr = "192.168.0.104";     // the IP address of your Raspberry PI

var server_addr = "172.16.200.187"; // the IP address of your Raspberry PI

var refreshIntervalId;
var toggle = false;
function client(input) {
  const net = require("net");

  const client = net.createConnection(
    { port: server_port, host: server_addr },
    () => {
      // 'connect' listener.
      console.context().log("connected to server!");
      // send the message
      client.write(`${input}\r\n`);
    }
  );
  // get the data from the server
  client.on("data", (data) => {
    strData = data.toString();
    arr = strData.split("-");
    document.getElementById("direction").innerHTML = arr[0];
    document.getElementById("ulrasonic_data").innerHTML = arr[1];
    document.getElementById("temperature").innerHTML = arr[2];
    document.getElementById("intruderGif").src =
      "./uploads/intruder.gif?" + new Date().getTime();

    client.end();
    client.destroy();
  });
  client.on("end", () => {
    console.log("disconnected from server");
  });
}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {
  e = e || window.event;

  if (e.keyCode == "87") {
    // up (w)
    document.getElementById("upArrow").style.color = "green";
    client("forward");
  } else if (e.keyCode == "83") {
    // down (s)
    document.getElementById("downArrow").style.color = "green";
    client("reverse");
  } else if (e.keyCode == "65") {
    // left (a)
    document.getElementById("leftArrow").style.color = "green";
    client("left");
  } else if (e.keyCode == "68") {
    // right (d)
    document.getElementById("rightArrow").style.color = "green";
    client("right");
    c;
  } else if (e.keyCode == "81") {
    // camera check (q)
    document.getElementById("rightArrow").style.color = "green";
    client("cameraCheck");
    c;
  }
}

// reset the key to the start state
function resetKey(e) {
  e = e || window.event;

  document.getElementById("upArrow").style.color = "grey";
  document.getElementById("downArrow").style.color = "grey";
  document.getElementById("leftArrow").style.color = "grey";
  document.getElementById("rightArrow").style.color = "grey";
}

// update data for every 50ms
function update_data() {
  toggle = !toggle;

  if (toggle) {
    refreshIntervalId = setInterval(function () {
      // get image from python server
      client("update");
    }, 500);
  } else {
    clearInterval(refreshIntervalId);
  }
}
