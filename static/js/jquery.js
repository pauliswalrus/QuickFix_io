$(document).ready(function() {

    //
    //    $('#fade').css('background-color', '#E46D4E');
    //    $('#fade').css('color', 'white');
    //
    //    $('#fade').fadeOut(500);
    //    $('#fade').fadeIn(500);
    //    $('#fade').fadeOut(500);
    //
    //    $('#fade2').css('background-color', '#E46D4E');
    //    $('#fade2').css('color', 'white');
    //
    //
    // $('#fade').on('click', function() {
    //     $('#fade').fadeOut(1000);
    //     $('#fade').fadeIn(1000);
    // });
    //
    // $('#send_message').on('click', function() {
    //     $('#fade2').fadeIn(500);
    //     $('#fade2').fadeOut(500);
    //     $('#fade2').fadeIn(500);

    // });
/*

Admin portal functions

 */

//update room
    $('.updateButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        var title = $('#titleInput'+room_id).val()

        var content = $('#contentInput'+room_id).val()

        req = $.ajax({
           url : '/updateRoom',
           type : 'POST',
           data : { name : name, title : title, content : content, id : room_id }

        });

        req.done(function(data) {

            $('#roomSection'+room_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber'+room_id).text(data.room_name);

        });




    })
// also used in private chat
//make room private
    $('.privateButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/privateRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("This Room is Private!")
        $('.privateButton').fadeOut(200);
        $('.publicButton').fadeIn(200);



    })
//also used in private chat
//public room
    $('.publicButton').on('click',function () {

        var room_id = $(this).attr('room_id');
        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/publicRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("This Room is Public!")
        $('.publicButton').fadeOut(200);
        $('.privateButton').fadeIn(200);



    })




//delete room
    $('.deleteButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        var r = confirm("Delete Room?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteRoom',
                type: 'POST',
                data: {name: name, id: room_id}

            });
            alert("Room Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })

//approve tutor
    $('.approveTutor').on('click',function () {

        var user_id = $(this).attr('user_id');


        var r = confirm("Approve Tutor?");

        if (r == true) {


            req = $.ajax({
                url: '/approveTutor',
                type: 'POST',
                data: {id: user_id}

            });
            alert("Tutor Approved!")
            location.reload();

        } else {
            //nothing happens
        }

    })


//deny tutor
    $('.denyTutor').on('click',function () {

        var user_id = $(this).attr('user_id');
        var comments = $("#appComments").val();

        var r = confirm("Deny This Tutor?");

        if (r == true) {

            req = $.ajax({
                url: '/denyTutor',
                type: 'POST',
                data: {id: user_id, comments: comments}

            });
            alert("Tutor Denied!")
            location.reload();


        } else {
            //nothing happens
        }


    })

//delete user
    $('.deleteUser').on('click',function () {

        var user_id = $(this).attr('user_id');
        var r = confirm("Delete User?");

        if (r == true) {



        req = $.ajax({
           url : '/deleteUser',
           type : 'POST',
           data : { id : user_id }

        });
        alert("User Deleted!")
        location.reload();
         } else {
            //nothing happens
        }

    })

    //open edit user
    $('.editUser').on('click',function () {

        var user_id = $(this).attr('user_id');

        $('.modal_editUser').show();


    })

        //close edit user
    $('.closeWindow').on('click',function () {

        var user_id = $(this).attr('user_id');

        $('.modal_editUser').hide();


    })


//edit user
    $('.editUserForm').on('click',function () {

        var user_id = $(this).attr('user_id');

        var firstname = $('#firstName'+user_id).val();
        var lastname = $('#lastName'+user_id).val();
        var username = $('#userName'+user_id).val();


        req = $.ajax({
           url : '/editUser',
           type : 'POST',
           data : { firstname : firstname, lastname : lastname, username : username, id : user_id }

        });
        alert("User Edited!");

        location.reload();


    })




//delete chat logs
    $('.deleteLogs').on('click',function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Delete Chat Logs?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteLogs',
                type: 'POST',
                data: {id: room_id}

            });
            alert("Chat Log Cleared!");
            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);
        } else {

            //nothing happens
        }



    })

    //delete chat logs
    $('.deleteRoomUploads').on('click',function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Delete Room Uploads?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteRoomUploads',
                type: 'POST',
                data: {id: room_id}

            });
            alert("Room Uploads Cleared!");
            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);

        } else {

        }


    })





});