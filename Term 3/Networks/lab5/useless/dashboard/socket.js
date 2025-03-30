var INFOs = [];
var log = document.getElementById("log");
var newsHeader = document.getElementById("newsHeader");
var NEWs = document.getElementsByClassName("news")[0];
var temp = document.getElementById("InfoTemplate")

/**
 * 
 * @param {Node} node 
 * @param {{header : "", text : "", id : 0}} data 
 */
function changeNode(node, data) {
  node.querySelector('.header').innerHTML = data.Number+1 + ". " + data.header
  node.querySelector('.text').textContent = data.text
  return node
}

function clearNews(){
  document.getElementsByClassName("new").length
  l = document.getElementsByClassName("new").length
  for (let i = 0; i < l; i++) {
    document.getElementsByClassName("new")[0].remove() 
  }
  INFOs = []
}
function handleInfo(data) {
  const newInfo = JSON.parse(data)

  // Update existing infos
  for (let i = 0; i < INFOs.length; i++) {
    const info = INFOs[i];
    if (info.id == newInfo.id && document.getElementById(newInfo.id) != null) {
      newInfo.Number = i
      changeNode(document.getElementById(newInfo.id), newInfo)
      return
    }
    
  }

  
  let clon = temp.content.cloneNode(true);
  const newDiv = clon.querySelector('.new');
  newDiv.id = newInfo.id
  newInfo.Number = INFOs.length
  NEWs.appendChild(changeNode(newDiv, newInfo))
  INFOs.push(document.getElementById(newDiv.id))
  
}

function reconnect () {
  // Wait for 2 seconds and reconnect
  setTimeout(() => {
    initSocket()
  }, 2000);
}

function initSocket(){
  var ip = "185.102.139.168"
  var port = "4411"
  var socket = new WebSocket("ws://" + ip + ":" + port + "/ws")

  socket.onopen = function() {
      log.textContent = "\nСоединение установлено.";
    };
  
  socket.onclose = function(event) {
      if (event.wasClean) {
        console.log('Соединение закрыто чисто');
      } else {
        console.log('Обрыв соединения'); // например, "убит" процесс сервера
      }
      console.log('Код: ' + event.code + ' причина: ' + event.reason);
      // socket.close()
      log.textContent = "\nСоединение закрыто.";
      reconnect()
    };
    
  socket.onmessage = function(event) {
      console.log("Получены данные " + event.data);
      if (event.data == "clear") {
        clearNews()
      } else {
        handleInfo(event.data)
        newsHeader.textContent = "News: " + INFOs.length

      }


    };
    
  socket.onerror = function(error) {
      console.log("Ошибка " + error.message);
      log.textContent = "\nОшибка соединения";
      // socket.close()
      // reconnect()
    };
}

window.onload = initSocket