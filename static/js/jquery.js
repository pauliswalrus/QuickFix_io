$(document).ready(function() {

       $('#fade').css('background-color', '#E46D4E');
       $('#fade').css('color', 'white');

       $('#fade').fadeOut(500);
       $('#fade').fadeIn(500);
       $('#fade').fadeOut(500);

       $('#fade2').css('background-color', '#E46D4E');
       $('#fade2').css('color', 'white');


    $('#fade').on('click', function() {
        $('#fade').fadeOut(1000);
        $('#fade').fadeIn(1000);
    });

    $('#send_message').on('click', function() {
        $('#fade2').fadeIn(500);
        $('#fade2').fadeOut(500);
        $('#fade2').fadeIn(500);



    });

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


    $('.privateButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/privateRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("this room is private!")
        $('.privateButton').fadeOut(200);
        $('.publicButton').fadeIn(200);



    })


    $('.publicButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/publicRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("this room is public!")
        $('.publicButton').fadeOut(200);
        $('.privateButton').fadeIn(200);



    })

       $('.deleteButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/deleteRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("Room Deleted!")
        location.reload();



    })


    $('.approveTutor').on('click',function () {

        var user_id = $(this).attr('user_id');

        req = $.ajax({
           url : '/approveTutor',
           type : 'POST',
           data : { id : user_id }

        });

        req.done(function(data) {
            alert(data.tutor_status);

            $('#memberNumber'+user_id).text(data.tutor_status);
            $('#tutorSection'+user_id).fadeOut(1000).fadeIn(1000);

            location.reload();

        });


    })

    $('.denyTutor').on('click',function () {

        var user_id = $(this).attr('user_id');

        var comments = $('#appComments'+user_id).val();

        req = $.ajax({
           url : '/denyTutor',
           type : 'POST',
           data : { id : user_id, comments : comments}

        });
        location.reload();


    })




});