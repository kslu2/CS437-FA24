var server_port = 65432;
//var server_addr = "192.168.0.104";     // the IP address of your Raspberry PI
var server_addr = "100.69.37.118"; // the IP address of your Raspberry PI

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
    console.log("hi hi");
    document.getElementById("direction").innerHTML = arr[0];
    document.getElementById("ulrasonic_data").innerHTML = arr[1];
    document.getElementById("temperature").innerHTML = arr[2];
    document.getElementById("intruderGif").src = "./uploads/intruder.gif?t=" + new Date().getTime();
    document.getElementById("intruderImage").src = "./uploads/intruder.jpg?t=" + new Date().getTime();
    console.log(document.getElementById("intruderGif").src);
    console.log(document.getElementById("intruderImage").src);

  });
  client.on("end", () => {
    console.log("disconnected from server");
  });
}

function updateImages() {
  setInterval(function () {
    document.getElementById("intruderGif").src =
      "./uploads/intruder.gif?t=" + new Date().getTime();
        document.getElementById("intruderImage").src = "./uploads/intruder.jpg?t=" + new Date().getTime();
        console.log(document.getElementById("intruderGif").src);
        console.log(document.getElementById("intruderImage").src);
    }, 2000); // Updates every 500ms (half a second)
}

updateImages();
