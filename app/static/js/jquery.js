$(document).ready(function() {

       $('#fade').css('background-color', '#E46D4E');
       $('#fade').css('color', 'white');

       $('#fade').fadeOut(500);
       $('#fade').fadeIn(500);
       $('#fade').fadeOut(500);


    $('#fade').on('click', function() {
        $('#fade').fadeOut(1000);
        $('#fade').fadeIn(1000);
    });

    $('#send_message').on('click', function() {
        $('#fade').fadeIn(500);
        $('#fade').fadeOut(500);
    });

    $('.updateButton').on('click',function () {

        var post_id = $(this).attr('post_id');

        var name = $('#nameInput'+post_id).val();

        var title = $('#titleInput'+post_id).val()

        var content = $('#contentInput'+post_id).val()

        req = $.ajax({
           url : '/updateRoom',
           type : 'POST',
           data : { name : name, title : title, content : content, id : post_id }

        });



        req.done(function(data) {

            $('#roomSection'+post_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber'+post_id).text(data.room_name);

        });




    })


    $('.deleteButton').on('click',function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput'+room_id).val();

        req = $.ajax({
           url : '/privateRoom',
           type : 'POST',
           data : { name : name, id : room_id }

        });
        alert("this room is private!")
        $('.deleteButton').fadeOut(200);



    })

    $('.timerButton').on('click',function () {

       var start = new Date;

        setInterval(function() {
        $('#timerValue').text((new Date - start) / 1000-2 + " Seconds");
        }, 1000);

        //var room_title = $('#room_Input'+post_id).val();

    })




});