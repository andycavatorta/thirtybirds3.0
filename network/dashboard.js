/*

"app_git_timestamp": "Thu Dec 17 14:43:35 2020 -0500", 
"app_scripts_version(": 0.0, 
"connections": [false, {"dervishes-1": false, "dervishes-2": false, "dervishes-3": false, "dervishes-4": false, "dervishes-5": false, "dervishes-6": false, "dervishes-7": false}]}]

*/



/* ========== G L O B A L S ========== */
var SVG_NS = "http://www.w3.org/2000/svg";
var HTML_NS = "http://www.w3.org/1999/xhtml"
var panel = null;
var hGrid = [30, 230, 430, 630, 830, 1030, 1230, 1430, 1630, 1830, 2030, 2230, 2430, 2630, 2820];
var vGrid = [5, 45, 85, 125, 165, 505, 545, 585];
var websocket;
var exceptionDisplayState = false;

/* ========== U T I L S ========== */
function setAttributes(obj, att_a) {
    for (var ai = 0; ai < att_a.length; ai++) {
        obj.setAttribute(att_a[ai][0], att_a[ai][1]);
    }
}

/* ========== C O N S T R U C T O R S ========== */

function foo(e) {
    console.log(this)
}





/* ========== V I E W S ========== */

function toggleExceptions() {
    exceptionDisplayState = !exceptionDisplayState
    document.getElementById("exceptionsContainer").style.display = exceptionDisplayState ? "flex" : "none"
}

/* ========== D A T A ========== */

var data = {
    exceptions: "",
    status_messages: ""
}



/* ========== C O N T R O L L E R ========== */

function update_exceptions(message) {
    data.exceptions = data.exceptions + "\n" + message;
    exception_display.update(data.exceptions) // todo: update should pull from data.
}
function update_status(message) {
    data.status_messages = data.status_messages + "\n" + message;
    status_display.update(data.status_messages) // todo: update should pull from data.
}
timers = {
    retry_connection: window.setInterval(try_to_connect, 1000)
}


/* ========== N E T W O R K  ========== */

function websocket_connect() {
    console.log("connecting to wesockets")
    try {
        //console.log("readyState=",websocket.readyState)
        url = "ws://" + location.hostname + ":8001/"
        websocket = new WebSocket(url);
        websocket.onopen = function (evt) { websocket_open(evt) };
        websocket.onclose = function () { websocket_close() };
        websocket.onmessage = function (evt) { websocket_message_handler(evt) };
        websocket.onerror = function (evt) { websocket_error_handler(evt) };
    }
    catch (e) {
        console.log(e)
        console.log("connection failed")
    }
}

function websocket_send(evt) {
    websocket.send("Sample data ")
    console.log(evt)
}
function websocket_open(evt) {
    console.log("send test websocket message")
    websocket.send("Sending test message from dashboard client")

    window.clearInterval(timers.retry_connection)
    timers.retry_connection = false;
    console.log(evt)
}
function websocket_close() {
    if (timers.retry_connection == false) {
        //timers.retry_connection = window.setInterval(try_to_connect, 1000);
    }
    console.log("closed")
}

function sendTrigger(command) {
    console.log("Sending command ", command)
    websocket.send(command)
}



function updateDashboardValues(data) {
    console.log("Updating values  ")
    document.getElementById("hostname").innerText = data.hostname
    document.getElementById("local_ip").innerText = data.local_ip
    document.getElementById("global_ip").innerText = data.global_ip
    document.getElementById("connections").innerText = data.connections[0]
    document.getElementById("os_version").innerText = `${data.os_version[0]} ${data.os_version[1]}`
    
    document.getElementById("scripts_version").innerText = data.tb_scripts_version
    document.getElementById("core_temp").innerText = data.core_temp + "C"

    document.getElementById("system_cpu").innerText = data.system_cpu + "%"
    document.getElementById("system_disk").innerText = Math.round(data.system_disk[0]/1000000000)+"GB/"+Math.round(data.system_disk[1]/1000000000)+"GB"

    document.getElementById("memory_free").innerText = Math.round(data.memory_free[0]/1000000000)+"GB/"+Math.round(data.memory_free[1]/1000000000)+"GB"
    document.getElementById("wifi_strength").innerText = data.wifi_strength

}

function websocket_message_handler(evt) {
    var topic_data = JSON.parse(evt.data);
    console.log("New websocket msg " + topic_data[1])


    var topic = topic_data[0]
    var data = topic_data[1]
    switch (topic) {
        case "status":
            updateDashboardValues(data)
            break;
    }
    console.log("Sending data back")
    try {
    websocket.send("{'a':'Sample Send'}")
    } catch (e) {
        console.log("got error in sendings")
        console.log(e)
    }

}
function websocket_error_handler(evt) {
    console.log("websocket_error_handler", evt)
    if (timers.retry_connection == false) {
        //timers.retry_connection = window.setInterval(try_to_connect, 1000);
    }
}

function try_to_connect() {
    try {
        websocket_connect()
    }
    catch (e) {
        console.log("connection failed")
    }
}

/* ========== I N I T ========== */

function init() {
    console.log("established init")
    panel = document.getElementById("top_level");
    test_data = {
        "system_uptime": "2021-04-29 16:02:33",
        "system_cpu": 0, 
        "memory_free": [3304296000, 3914088000],
         "system_disk": [ 2677698560, 7583248384 ], 
         "core_temp": 47, 
         "os_version": ["ubuntu", "20.10"], 
         "wifi_strength": 0,
        "tb_git_timestamp": "Thu Apr 29 14:06:52 2021 -0400",
        "tb_scripts_version": 0,
        "app_git_timestamp": "Thu Apr 22 14:17:14 2021 -0400",
        "hostname" : "dervishes-1",
        "global_ip" : "204.97.222.2",
        "local_ip": "196.168.5.45",
        "connections" : [true]
    }
    updateDashboardValues(test_data)


    //   var h_pos = 0;

    //   new Form_Text_Input(parent,foo,"topic",hGrid[6],vGrid[2]);
    //   new Form_Text_Input(parent,foo,"data",hGrid[7],vGrid[2]);

    //   h_pos = 0;
    //   exception_display = new Text_Area(panel, hGrid[h_pos], vGrid[4], 330, 2800);
    //   status_display = new Text_Area(panel, hGrid[h_pos], vGrid[6], 330, 2800);

    //   view.ti_hostname.button.update("dervishes-1")
    //   view.ti_local_ip.button.update("196.168.5.45")
    //   view.ti_global_ip.button.update("204.97.222.2")
    //   view.ti_connections.button.update("true")
    //   view.ti_os_version.button.update("Ubuntu 20")
    //   view.ti_scripts_version.button.update("8")
    //   view.ti_git_timestamp.button.update("12 12 12 12 12 ")
    //   view.ti_exceptions.button.update("++")
    //   view.ti_core_temp.button.update("3.3vdc")
    //   view.ti_system_cpu.button.update("34%")
    //   view.ti_system_uptime.button.update("23452345")
    //   view.ti_system_disk.button.update("2342354MB")
    //   view.ti_memory_free.button.update("23463MB")
    //   view.ti_wifi_strength.button.update("65%")

    //   update_exceptions("exception 1 fdasasdf")
    //   update_exceptions("exception 2 ccccccccccccc")

    //   update_status("status 1 fdasasdf")
    //   update_status("status 2 ccccccccccccc")

    //websocket_connect()
}