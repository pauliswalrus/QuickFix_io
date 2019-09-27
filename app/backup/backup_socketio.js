document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    let room = "Lounge";
    joinRoom("Lounge");



    /*socket.on('connect', () => {
        socket.send("I am connected");
    });
    */
    /*

      //Displays incoming messages
    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const span_title = document.createElement("span");
        const br = document.createElement('br');

        if (data.username) {
            span_username.innerHTML = data.username;
            span_timestamp.innerHTML = data.time_stamp;
            span_title.innerHTML = " - student";

            p.innerHTML = span_username.outerHTML + span_title.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
            document.querySelector('#display-message-section').append(p);
            //console.log(`Message received: ${data}`)
        } else {
            printSysMsg(data.msg);
        }


    });
     */
    //Displays incoming messages
    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        //const span_title = document.createElement("span");
        const br = document.createElement('br');

        if (data.username) {
            span_username.innerHTML = data.username;
            span_timestamp.innerHTML = data.time_stamp;
            //span_title.innerHTML = " - student";

            p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
            document.querySelector('#display-message-section').append(p);
            //console.log(`Message received: ${data}`)
        } else {
            printSysMsg(data.msg);
        }


    });

    /*
    socket.on('some-event', data => {
        console.log(data);
    }); */

    //Room selection test
    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newRoom = p.innerHTML;
            if (newRoom == room) {
                msg = `You are already in ${room} room.`
                printSysMsg(msg);
            } else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        }
    });

      // send message
    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg': document.querySelector('#user_message').value, 'username' : username, 'room': room });

        //clear input area
        document.querySelector('#user_message').value = '';

    }

    //create join different room
    document.querySelector('#join_room').onclick = () => {

        room = document.querySelector('#room_to_join').value;

        document.querySelector('#room_to_join').value = '';

        joinRoom(room);
    }

    document.querySelector('#new_room')

    //socket.on('create', function (room) {
    // socket.join(room);
    //});

    //leave room
    function leaveRoom(room) {
        socket.emit('leave', {'username': username, 'room': room});


    }

    //join room
    function joinRoom(room) {
        socket.emit('join', {'username': username, 'room': room});

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

