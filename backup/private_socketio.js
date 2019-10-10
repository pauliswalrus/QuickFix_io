document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');

    //Displays incoming messages
    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');

        const br = document.createElement('br');

        if (data.username == username) {

            p.setAttribute("class", "my-msg");

            span_username.setAttribute("class", "my-username");
            span_username.innerHTML = data.username;

            span_timestamp.setAttribute("class", "timestamp");
            span_timestamp.innerHTML = data.time_stamp;
            //span_title.innerHTML = " - student";

            p.innerHTML = span_username.outerHTML + span_timestamp.outerHTML + br.outerHTML + data.msg;
            //p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
            document.querySelector('#display-message-section').append(p);
            //console.log(`Message received: ${data}`)
        }
        else if (typeof data.username !=='undefined') {
            p.setAttribute("class", "others-msg");

            span_username.setAttribute("class", "other-username");
            span_username.innerText = data.username;

            span_timestamp.setAttribute("class", "other-timestamp");
            span_timestamp.innerText = data.time_stamp;

            p.innerHTML = span_timestamp.outerHTML + span_username.outerHTML + br.outerHTML + data.msg;
            document.querySelector('#display-message-section').append(p);

            //p.innerHTML = span_timestamp.outerHTML + span_username + br.outerHTML + data.msg;
        }
        else {
            printSysMsg(data.msg);
        }


    });

      // send message
    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg': document.querySelector('#user_message').value, userName, 'room': room });
        //clear input area
        document.querySelector('#user_message').value = '';

    }


    //leave room
    function leaveRoom(room) {
        socket.emit('left', {'username': username, 'room': room});
        socket.disconnect();


    }

    //join room
    function joinRoom(room) {
        socket.emit('joined', {'username': username, 'room': room});

        //document.querySelector('.select-room' + CSS.escape(room)).style.color = "#ffc107";
        //document.querySelector('.select-room').style.backgroundColor = "white";

        //document.querySelector('#sidebar').style.backgroundColor = "#ffc107";
        //clear message area
        document.querySelector('#room-name').innerHTML = room;
        document.querySelector('#display-message-section').innerHTML = '';
        //document.querySelector('#user_message').focus();
    }




    function printSysMsg(msg) {
        const p = document.createElement('p');
        p.innerHTML = msg;
        document.querySelector('#display-message-section').append(p);

    }

})