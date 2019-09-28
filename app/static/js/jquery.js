$(document).ready(function() {

    //alert('jquery is ready to go');

    //$('h1').hide();
       $('#fade').css('background-color', '#E46D4E');
       $('#fade').css('color', 'white');

       $('#fade').fadeOut(500);
       $('#fade').fadeIn(500);
       $('#fade').fadeOut(500);

    //$('h1').css('color', 'red');
    //$('p').css('color', 'green');

    //$('div#one').css('color', 'orange');
    //$('#two').css('color', 'purple');


    //$('.content').css('color', 'red');
    //$('p.nav').css('color', 'pink');


    //$('#header').on('click', function() {


        //$('#language').val('jQuery')

    //});

    // $('#language').on('change', function() {
    //     var input_value = $(this).val();
    //     alert('the input has been changed to ' + input_value);
    //
    // });

    // $('#name').val('Anthony Herbert');

    $('#fade').on('click', function() {
        $('#fade').fadeOut(1000);
        $('#fade').fadeIn(1000);
    });

    $('#send_message').on('click', function() {
        $('#fade').fadeIn(500);
        $('#fade').fadeOut(500);
    });

});