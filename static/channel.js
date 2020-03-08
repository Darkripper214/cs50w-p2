document.addEventListener("DOMContentLoaded", () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

    // When connected, configure button
    socket.on("connect", () => {

        // Notify the server user has joined
        socket.emit("joined");

        // Forget user"s last channel when clicked on "add channel"
        document.querySelector("#newChannel").addEventListener("click", () => {
            localStorage.removeItem("lastChannel");
        });

        // When user leaves channel redirect to "/"
        document.querySelector("#leave").addEventListener("click", () => {

            // Notify the server user has left
            socket.emit("left");

            localStorage.removeItem("lastChannel");
            window.location.replace("/");
        })
        // When user move to other channel, emit message
        var changeChannel = document.querySelectorAll(".changeChannel");
        for (var i = 0; i < changeChannel.length; i++) {
          changeChannel[i].addEventListener('click', () => {
            socket.emit("left");
          })
        };

        // Forget user"s last channel when logged out
        document.querySelector("#logout").addEventListener("click", () => {
            localStorage.removeItem("lastChannel");
        });

        // "Enter" key on textarea also sends a message
        // https://developer.mozilla.org/en-US/docs/Web/Events/keydown
        document.querySelector("#comment").addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send-button").click();
            }
        });

        // Send button emits a "message sent" event
        document.querySelector("#send-button").addEventListener("click", () => {

            // Save time in format HH:MM:SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Save user input
            let msg = document.getElementById("comment").value;

            socket.emit("sendMessage", msg, timestamp);

            // Clear input
            document.getElementById("comment").value = "";
        });
    });

    // When user joins a channel, add a message and on users connected.
    socket.on("status", data => {

        // Broadcast message of joined user.
        let row = "<" + `${data.msg}` + ">"
        document.querySelector("#chat").value += row + "\n";

        // Save user current channel on localStorage
        localStorage.setItem("lastChannel", data.channel)
    })

    // When a message is announced, add it to the textarea.
    socket.on("announceMessage", data => {
        // Format message
        let row = "[" + `${data.timestamp}` + "] - " + "(" + `${data.user}` + "):  " + `${data.msg}`
        document.querySelector("#chat").value += row + "\n"
    })

});
