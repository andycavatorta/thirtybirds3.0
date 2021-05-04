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
var THIRTYSECONDS = 30000

/* ========== U T I L S ========== */
function setAttributes(obj, att_a) {
    for (var ai = 0; ai < att_a.length; ai++) {
        obj.setAttribute(att_a[ai][0], att_a[ai][1]);
    }
}

let button = document.getElementById("button");

//In Progress Alert Bar 
function alertHandler(cmd) {
    let alerts = document.getElementById("alert-container");
    console.log(alerts.childNodes)
    setTimeout(function () {
        console.log(alerts.childNodes)
        alerts.childNodes[0].remove()

    }, 2000);

    if (alerts.childElementCount < 2) {
        // Create alert box
        let alertBox = document.createElement("div");
        alertBox.classList.add("alert-msg", "slide-in");

        // Add message to alert box
        let alertMsg = document.createTextNode(cmd);
        alertBox.appendChild(alertMsg);

        // Add alert box to parent
        alerts.insertBefore(alertBox, alerts.childNodes[0]);

    }
}

// button.addEventListener("click", alertHandler);


Date.prototype.addHours = function(h) {
    this.setTime(this.getTime() + (h*60*60*1000));
    return this;
  }

//https://stackoverflow.com/questions/21294302/converting-milliseconds-to-minutes-and-seconds-with-javascript
// In Progress Clean way of Showing last timestamp
// function getTimeSinceLastTimestamp(last_seen_timestamp) {
//     console.log("formatting date")
//     console.log(last_seen_timestamp)
//     var lst_date = new Date(last_seen_timestamp)
//     console.log(lst_date)
//     var current_datetime = new Date()
//     current_datetime.addHours(4)
//     console.log(current_datetime)
//     var millis = current_datetime.getTime() - lst_date.getTime()


//     if (millis > THIRTYSECONDS) {
//         document.getElementById("last_seen_timestamp").classList.remove("healthyValue")
//         document.getElementById("last_seen_timestamp").classList.add("dangerValue")
//     } else {
//         document.getElementById("last_seen_timestamp").classList.remove("dangerValue")
//         document.getElementById("last_seen_timestamp").classList.add("healthyValue")

//     }

//     console.log("millis : ",millis)
//     var minutes = Math.floor(millis / 60000);
//     var seconds = ((millis % 60000) / 1000).toFixed(0);

//     var minSeconds = minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
//     console.log(minSeconds)
//     return minSeconds;
//   }

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
    try {
        websocket.send("Sending test message from dashboard client")

    } catch (e) {
        console.log(e)
    }

    window.clearInterval(timers.retry_connection)
    timers.retry_connection = false;
    console.log(evt)
}
function websocket_close() {
    if (timers.retry_connection == false) {
        //timers.retry_connection = window.setInterval(try_to_connect, 1000);
    }
    // console.log("closed")
}

function sendTrigger(command) {
    console.log("Sending command ", command)
    try{
        websocket.send(command)
        alertHandler(`Executed command ${command}`)

    } catch (e) {
        alertHandler(`Could not execute command ${command}`)
    }
}



function updateDashboardValues(data) {

    document.getElementById("hostname").innerText = data.hostname
    document.getElementById("local_ip").innerText = data.local_ip
    document.getElementById("global_ip").innerText = data.global_ip
    document.getElementById("connections").innerText = data.connections[0]
    document.getElementById("os_version").innerText = `${data.os_version[0]} ${data.os_version[1]}`

    document.getElementById("app_git_timestamp").innerText = data.app_git_timestamp
    document.getElementById("core_temp").innerText = data.core_temp + "C"

    document.getElementById("system_cpu").innerText = data.system_cpu + "%"
    document.getElementById("system_disk").innerText = Math.round(data.system_disk[0] / 1000000000) + "GB/" + Math.round(data.system_disk[1] / 1000000000) + "GB"

    document.getElementById("memory_free").innerText = Math.round(data.memory_free[0] / 1000000000) + "GB/" + Math.round(data.memory_free[1] / 1000000000) + "GB"
    document.getElementById("tb_git_timestamp").innerText = data.tb_git_timestamp
    document.getElementById("last_seen_timestamp").innerText = data.msg_timestamp


}

function websocket_message_handler(evt) {
    var topic_data = JSON.parse(evt.data);
    // console.log("New Websocket Message")
    // console.log(topic_data[1])


    var topic = topic_data[0]
    var data = topic_data[1]
    switch (topic) {
        case "status":
            updateDashboardValues(data)
            break;
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
        "system_uptime": "",
        "system_cpu": 0,
        "memory_free": [0, 0],
        "system_disk": [0, 0],
        "core_temp": 0,
        "os_version": ["Waiting", "For Data"],
        "wifi_strength": 0,
        "tb_git_timestamp": "2021-05-03 17:45:29.605893",
        "tb_scripts_version": 0,
        "app_git_timestamp": "2021-05-03 17:45:29.605893",
        "hostname": "Waiting For Data",
        "global_ip": "0.0.0.0",
        "local_ip": "0.0.0.0",
        "connections": [false],
        "msg_timestamp": "2021-05-03 17:45:29.605893"
    }
    updateDashboardValues(test_data)


}