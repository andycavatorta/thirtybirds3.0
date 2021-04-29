/*

"app_git_timestamp": "Thu Dec 17 14:43:35 2020 -0500", 
"app_scripts_version(": 0.0, 
"connections": [false, {"dervishes-1": false, "dervishes-2": false, "dervishes-3": false, "dervishes-4": false, "dervishes-5": false, "dervishes-6": false, "dervishes-7": false}]}]

*/



/* ========== G L O B A L S ========== */
var SVG_NS ="http://www.w3.org/2000/svg";
var HTML_NS = "http://www.w3.org/1999/xhtml"
var panel = null;
var hGrid = [30,230,430, 630, 830, 1030, 1230, 1430, 1630, 1830, 2030, 2230, 2430, 2630, 2820];
var vGrid = [5, 45, 85, 125, 165, 505, 545, 585];

/* ========== U T I L S ========== */
function setAttributes(obj, att_a){
  for(var ai=0; ai<att_a.length; ai++){
    obj.setAttribute(att_a[ai][0],att_a[ai][1]);
  }
}

/* ========== C O N S T R U C T O R S ========== */

function foo(e) {
  console.log(this)
}

function Button(parent,label,action_ref,x,y,w) {
  if(!w){
    var w=190;
  }
  var h=30;
  this.button = document.createElementNS( SVG_NS, "g" );
  var rect = document.createElementNS( SVG_NS, "rect" );
  setAttributes(rect, [
      ["x",x],
      ["y",y],
      ["width",w],
      ["height",h],
      ["class","button"]
    ]
  )
  var label_ns = document.createElementNS( SVG_NS, "text" );
  setAttributes(label_ns, [
      ["x",x+10],
      ["y",y+20],
      ["width",w],
      ["font-family", "Jura"],
      ["font-size", "16"],
      ["fill","#000000"],
      ["text-align", "center"]
    ]
  )
  var label_tn = document.createTextNode(label)
  label_ns.appendChild(label_tn);
  this.button.appendChild(label_ns);
  this.button.appendChild(rect);
  rect.style.cursor = "pointer";
  label_ns.style.cursor = "pointer";
  this.button.addEventListener("click", action_ref, true);
  parent.appendChild(this.button)
}

function Text_Header(parent,label,x,y,w) {
  if(!w){
    var w=190;
  }
  var h=30;
  this.button = document.createElementNS( SVG_NS, "g" );
  var rect = document.createElementNS( SVG_NS, "rect" );
  setAttributes(rect, [
      ["x",x],
      ["y",y],
      ["width",w],
      ["height",h],
      ["class","text_header_rect"]
    ]
  )
  var label_1_ns = document.createElementNS( SVG_NS, "text" );
  setAttributes(label_1_ns, [
      ["x",x+10],
      ["y",y+20],
      ["width",w/2],
      ["text-align", "center"],
      ["class","text_header"]
    ]

  )
  label_1_ns.appendChild(document.createTextNode(label));
  this.button.appendChild(rect);
  this.button.appendChild(label_1_ns);
  parent.appendChild(this.button)
}

function Text_Indicator(parent,x,y,w) {
  if(!w){
    var w=190;
  }
  var h=30;
  this.button = document.createElementNS( SVG_NS, "g" );
  this.button.label_ns = document.createElementNS( SVG_NS, "text" );
  setAttributes(this.button.label_ns, [
      ["x",x+10],
      ["y",y+20],
      ["width",w/2],
      ["font-family", "Jura"],
      ["font-size", "16"],
      ["fill","#000000"],
      ["text-align", "center"]
    ]
  )
  this.button.appendChild(this.button.label_ns);
  this.button.update = function(_text){

    while(this.label_ns.hasChildNodes()){
      this.label_ns.removeChild(this.label_ns.firstChild)
    }
    this.label_ns.appendChild(document.createTextNode(_text));
  }
  parent.appendChild(this.button)
}

function Form_Text_Input(parent,action_ref,placeholder,x,y,w) {
  if(!w){
    var w=190;
  }
  var fo = document.createElementNS( SVG_NS, "foreignObject")
  fo.style = "x:"+x+";y:"+y+";width:192;height:24;"
  //fo.setAttribute('x',x)
  //fo.setAttribute('y',y)
  var d = document.createElement('div')
  d.setAttribute('xmlns',HTML_NS)
  d.style = "display:block; x:1; y:1; width:192; height:22;";
  d.innerHTML = '<input>asdf</input>';
  var text_input = d.firstChild;
  text_input.setAttribute('class','form_text_input');
  text_input.setAttribute('placeholder',placeholder);
  fo.appendChild(d)
  text_input.addEventListener("change", action_ref);
  panel.appendChild(fo)
}

function Button(parent,label,action_ref,x,y,w) {
  if(!w){
    var w=190;
  }
  var h=30;
  this.button = document.createElementNS( SVG_NS, "g" );
  var rect = document.createElementNS( SVG_NS, "rect" );
  setAttributes(rect, [
      ["x",x],
      ["y",y],
      ["width",w],
      ["height",h],
      ["class","button"]
    ]
  )
  var label_ns = document.createElementNS( SVG_NS, "text" );
  setAttributes(label_ns, [
      ["x",x+10],
      ["y",y+20],
      ["width",w],
      ["font-family", "Jura"],
      ["font-size", "16"],
      ["fill","#000000"],
      ["text-align", "center"]
    ]
  )
  var label_tn = document.createTextNode(label)
  label_ns.appendChild(label_tn);
  this.button.appendChild(label_ns);
  this.button.appendChild(rect);
  rect.style.cursor = "pointer";
  label_ns.style.cursor = "pointer";
  this.button.addEventListener("click", action_ref, true);
  parent.appendChild(this.button)
}

function Text_Area(parent, x, y, height, width){
  var fo = document.createElementNS( SVG_NS, "foreignObject")
  fo.style = "x:"+x+";y:"+y+";width:"+width+";height:"+height+";";
  var d = document.createElement('div')
  d.setAttribute('xmlns',HTML_NS)
  d.style = "display:block; x:1; y:1; width:"+width+"px;height:"+height+"px;";
  d.innerHTML = '<textarea></textarea>';
  this.text_area = d.firstChild;
  this.text_area.setAttribute('class','form_text_area');
  this.text_area.style.height = height;
  this.text_area.style.width = width;

  fo.appendChild(d)
  panel.appendChild(fo)
  this.update = function(data){
    this.text_area.value = data;
  }
}


/* ========== D A T A ========== */

var data = {
  exceptions:"",
  status_messages:""
}

/* ========== V I E W  ========== */

var view = {
  make_labels:function(){
    var h_pos = 0;
    new Text_Header(panel,"host",hGrid[h_pos],vGrid[0]);
    new Text_Header(panel,"exceptions",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"git_timestamp",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"scripts version",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"os_version",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"local ip",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"global ip",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"connections",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"core_temp",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"system_cpu",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"system_uptime",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"system_disk",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"memory_free",hGrid[++h_pos],vGrid[0]);
    new Text_Header(panel,"wifi_strength",hGrid[++h_pos],vGrid[0]);
    h_pos = 0;
    new Text_Header(panel,"exceptions",hGrid[h_pos],vGrid[3]);
    new Text_Header(panel,"status",hGrid[h_pos],vGrid[5]);
  },
  make_indicators:function(){
    view.ti_hostname=new Text_Indicator(panel,hGrid[0],vGrid[1])
    view.ti_exceptions=new Text_Indicator(panel,hGrid[1],vGrid[1])
    view.ti_git_timestamp=new Text_Indicator(panel,hGrid[2],vGrid[1])
    view.ti_scripts_version=new Text_Indicator(panel,hGrid[3],vGrid[1])
    view.ti_os_version=new Text_Indicator(panel,hGrid[4],vGrid[1])
    view.ti_local_ip=new Text_Indicator(panel,hGrid[5],vGrid[1])
    view.ti_global_ip=new Text_Indicator(panel,hGrid[6],vGrid[1])
    view.ti_connections=new Text_Indicator(panel,hGrid[7],vGrid[1])
    view.ti_core_temp=new Text_Indicator(panel,hGrid[8],vGrid[1])
    view.ti_system_cpu=new Text_Indicator(panel,hGrid[9],vGrid[1])
    view.ti_system_uptime=new Text_Indicator(panel,hGrid[10],vGrid[1])
    view.ti_system_disk=new Text_Indicator(panel,hGrid[11],vGrid[1])
    view.ti_memory_free=new Text_Indicator(panel,hGrid[12],vGrid[1])
    view.ti_wifi_strength=new Text_Indicator(panel,hGrid[13],vGrid[1])
  },
  outer_container_expanded:true,
  outer_container_expansion:function(){
    var outer_container = document.getElementsByTagName('svg')[0];
    outer_container.setAttribute('height',(view.outer_container_expanded)?1250:80);
    view.outer_container_expanded = !view.outer_container_expanded;
  },
  make_buttons:function(){
    view.toggle_button = new Button(panel," ",view.outer_container_expansion,5,vGrid[1],20);
    view.reboot_button = new Button(panel,"reboot",foo,hGrid[0],vGrid[2]);
    view.shutdown_button = new Button(panel,"shutdown",foo,hGrid[1],vGrid[2]);
    view.tb_github_button = new Button(panel,"pull from github",foo,hGrid[2],vGrid[2]);
    view.tb_scripts_button = new Button(panel,"run update scripts",foo,hGrid[3],vGrid[2]);
    view.publish_button = new Button(panel,"publish",foo,hGrid[5],vGrid[2]);
  }
}

/* ========== C O N T R O L L E R ========== */

function update_exceptions(message){
  data.exceptions = data.exceptions + "\n" + message;
  exception_display.update(data.exceptions) // todo: update should pull from data.
}
function update_status(message){
  data.status_messages = data.status_messages + "\n" + message;
  status_display.update(data.status_messages) // todo: update should pull from data.
}
timers = {
  retry_connection:window.setInterval(try_to_connect, 1000)
}


/* ========== N E T W O R K  ========== */

function websocket_connect(){
  try{
      //console.log("readyState=",websocket.readyState)
      url = "ws://" + location.hostname +":8001/"
      websocket = new WebSocket(url);
      websocket.onopen = function(evt) { websocket_open(evt) };
      websocket.onclose = function() { websocket_close() };
      websocket.onmessage = function(evt) { websocket_message_handler(evt) };
      websocket.onerror = function(evt) { websocket_error_handler(evt) };
  }
  catch(e){
    console.log("connection failed")
  }
}

function websocket_send(evt){
  console.log(evt)
}
function websocket_open(evt){
  window.clearInterval(timers.retry_connection)
  timers.retry_connection = false;
  console.log(evt)
}
function websocket_close(){
  if(timers.retry_connection==false){
    //timers.retry_connection = window.setInterval(try_to_connect, 1000);
  }
  console.log("closed")
}
function websocket_message_handler(evt){
  var topic_data = JSON.parse(evt.data);
  var topic = topic_data[0]
  var data = topic_data[1]
  console.log(topic)
  console.log(data)
  switch(topic){
    case "status":
      view.ti_hostname.button.update(data.hostname)
      view.ti_local_ip.button.update(data.local_ip)
      view.ti_global_ip.button.update(data.global_ip)
      view.ti_connections.button.update(data.connections[0])
      view.ti_os_version.button.update(data.os_version[0]+" "+data.os_version[1])
      view.ti_scripts_version.button.update(data.tb_scripts_version)
      view.ti_git_timestamp.button.update(data.tb_git_timestamp)
      view.ti_exceptions.button.update("++")
      view.ti_core_temp.button.update(data.core_temp+"C")
      view.ti_system_cpu.button.update(data.system_cpu + "%")
      view.ti_system_uptime.button.update(data.system_uptime)
      view.ti_system_disk.button.update(Math.round(data.system_disk[0]/1000000000)+"GB/"+Math.round(data.system_disk[1]/1000000000)+"GB")
      view.ti_memory_free.button.update(Math.round(data.memory_free[0]/1000000000)+"GB/"+Math.round(data.memory_free[1]/1000000000)+"GB")
      break;
  }
}
function websocket_error_handler(evt){
  console.log("websocket_error_handler",evt)
  if(timers.retry_connection==false){
    //timers.retry_connection = window.setInterval(try_to_connect, 1000);
  }
}

function try_to_connect(){
  try{
    websocket_connect()
  }
  catch(e){
    console.log("connection failed")
  }
}

/* ========== I N I T ========== */

function init() {
  panel = document.getElementById( "top_level" ); 
  view.make_labels();
  view.make_indicators();
  view.make_buttons()
  var h_pos = 0;

  new Form_Text_Input(parent,foo,"topic",hGrid[6],vGrid[2]);
  new Form_Text_Input(parent,foo,"data",hGrid[7],vGrid[2]);

  h_pos = 0;
  exception_display = new Text_Area(panel, hGrid[h_pos], vGrid[4], 330, 2800);
  status_display = new Text_Area(panel, hGrid[h_pos], vGrid[6], 330, 2800);

  view.ti_hostname.button.update("dervishes-1")
  view.ti_local_ip.button.update("196.168.5.45")
  view.ti_global_ip.button.update("204.97.222.2")
  view.ti_connections.button.update("true")
  view.ti_os_version.button.update("Ubuntu 20")
  view.ti_scripts_version.button.update("8")
  view.ti_git_timestamp.button.update("12 12 12 12 12 ")
  view.ti_exceptions.button.update("++")
  view.ti_core_temp.button.update("3.3vdc")
  view.ti_system_cpu.button.update("34%")
  view.ti_system_uptime.button.update("23452345")
  view.ti_system_disk.button.update("2342354MB")
  view.ti_memory_free.button.update("23463MB")
  view.ti_wifi_strength.button.update("65%")

  update_exceptions("exception 1 fdasasdf")
  update_exceptions("exception 2 ccccccccccccc")

  update_status("status 1 fdasasdf")
  update_status("status 2 ccccccccccccc")

  //websocket_connect()
}