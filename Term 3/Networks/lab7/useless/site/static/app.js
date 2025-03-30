
const ws = new WebSocket("ws://185.104.251.226:1429/ws");
var ws_opened = false
ws.onopen = () => {
    console.log("Connected to server");
    ws_opened = true
    document.getElementById("submitBtn").disabled = false
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type == "display") {
        displayMessage(msg.body)
    } else if (msg.type == "setPrompt") {
        setPrompt(msg.body)
        addLine()

        // if (document.querySelectorAll(".output__commands").length == 0) {
        //     addLine()
        // }
    } else if (msg.type == "loginError") {
        // setPrompt(msg.body)
        document.getElementById("connectionStatus").textContent = "Wrong login!"

    } else if (msg.type == "loginSuccess") {
        document.getElementById("connectionStatus").textContent = "Connected"
        document.getElementById("submitBtn").disabled = true
        document.getElementById("console").style.visibility = "visible"
    } else {
        console.error("Unknown command from socket")
    }
};

ws.onclose = () => {
    console.log("Disconnected from server");
    ws_opened = false
    document.getElementById("submitBtn").disabled = true
    document.getElementById("connectionStatus").textContent = "Closed"
    document.getElementById("console").style.visibility = "hidden"
};

function sendLogin() {
    const serv = document.getElementById("server").value
    const user = document.getElementById("username").value
    const pswd = document.getElementById("password").value

    document.getElementById("connectionStatus").textContent = "Waiting..."

    const message = {
        type: "ftpLogin",
        body: [serv, user, pswd].join(" "),
    };
    ws.send(JSON.stringify(message));
}

function sendMessage(bodyr) {
    const message = {
        type: "ftpCommand",
        body: bodyr,
    };
    ws.send(JSON.stringify(message));
}

function displayMessage(msg, type) {
    const template = document.querySelector("#output-template");
    const outputDiv = document.querySelector(".output");
    if (msg[msg.length - 1] == "\n") {
        msg = msg.slice(0, -1)
    }
    msg.split("\n").forEach(splMsg => {

        const newCommand = template.content.cloneNode(true);
        newCommand.querySelector(".output__text").textContent = splMsg

        if (type) {
            newCommand.querySelector(".output__text").classList.add(type)
        }

        outputDiv.appendChild(newCommand);
    });
}


function clearCMD() {
    // const cmds = document.getElementsByClassName("output__line")
    const cmds = document.querySelectorAll(".output__line")

    for (const element of cmds) {
        element.remove()
    }

    addLine()
}

function setPrompt(prompt) {
    const template = document.querySelector("#command-template");
    template.content.querySelector(".output__prompt").textContent = prompt + " "
}

function addLine() {
    const outputDiv = document.querySelector(".output");
    const curs = document.querySelector(".cursor")
    if (curs) {
        curs.remove()
    }
    const template = document.querySelector("#command-template");
    const newCommand = template.content.cloneNode(true);
    outputDiv.appendChild(newCommand);
}


document.addEventListener("DOMContentLoaded", () => {
    const outputDiv = document.querySelector(".output");
    let commands = document.querySelectorAll(".output__commands");



    // Ensure the `output` div is focusable and listens for key events
    outputDiv.addEventListener("keydown", (event) => {
        event.preventDefault();

        // Ensure the main div is focused
        if (document.activeElement === outputDiv) {
            commands = document.querySelectorAll(".output__commands");
            if (commands.length != 0) {
                const lastCommand = commands[commands.length - 1];
                // Check for special keys
                if (event.key === "Backspace") {
                    lastCommand.textContent = lastCommand.textContent.slice(0, -1); // Remove last character
                } else if (event.key === "Enter") {
                    if (lastCommand.textContent == "clear") {
                        clearCMD()
                    } else if (lastCommand.textContent == "") {
                        addLine()
                    } else if (["upload", "download"].indexOf(lastCommand.textContent.split(" ")[0]) != -1) {
                        // sendMessage(lastCommand.textContent)
                        // Make popup
                    } else if (["ls", "rm", "cd", "mkdir", "exit", "rmdirall", "help", "rmdir"].indexOf(lastCommand.textContent.split(" ")[0]) != -1) {
                        displayMessage("Waiting...")
                        sendMessage(lastCommand.textContent)
                    } else {
                        displayMessage("Unknown command", "output__text_error")
                        addLine()
                    }

                } else if (event.key.length === 1) {
                    lastCommand.textContent += event.key; // Append typed character
                }
            }


        }
    });
});