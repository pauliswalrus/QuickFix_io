/* e.stopImmediatePropagation();
e.stopPropagation;

Admin portal functions */

$(document).ready(function () {


    //update room
    $('.updateButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

        var title = $('#titleInput' + room_id).val()

        var content = $('#contentInput' + room_id).val()

        req = $.ajax({
            url: '/updateRoom',
            type: 'POST',
            data: {name: name, title: title, content: content, id: room_id}

        });

        req.done(function (data) {

            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber' + room_id).text(data.room_name);

        });

    })

        //update room
    $('.updateButtonProfile').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

        var title = $('#titleInput' + room_id).val()


        req = $.ajax({
            url: '/updateRoomProfile',
            type: 'POST',
            data: {name: name, title: title, id: room_id}

        });

        req.done(function (data) {

            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber' + room_id).text(data.room_name);

        });

    })


    //make room private - private chat
    $('.privateButtonAdmin').on('click', function () {

        let room_id = $(this).attr('room_id');

        let name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/privateRoom',
            type: 'POST',
            data: {name: name, id: room_id}
        });
        alert("This Room is Private!")
        location.reload();
        // $('#memberNumber' + room_id).text(data.roo);
        // // $('#privateButton'+room_id).fadeOut(200);
        // // $('#publicButton'+room_id).fadeIn(200);
        //
        // $('#roomSection'+room_id).fadeOut(1000).fadeIn(1000);


    })

    //public room - private chat
    $('.publicButtonAdmin').on('click', function () {

        var room_id = $(this).attr('room_id');
        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/publicRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Public!")
        location.reload();
        // $('#privateButton'+room_id).fadeIn(200);
        // $('#publicButton'+room_id).fadeOut(200);
        //
        // $('#roomSection'+room_id).fadeOut(1000).fadeIn(1000);

    })

    //delete room
    $('.deletePost').on('click', function () {

        var post_id = $(this).attr('post_id');

        var r = confirm("Delete Post?");

        if (r == true) {

            req = $.ajax({
                url: '/deletePost',
                type: 'POST',
                data: {id: post_id}

            });
            alert("Post Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })


    //update room
    $('.updatePost').on('click', function () {

        var post_id = $(this).attr('post_id');

        var title = $('#titleInput' + post_id).val();

         var content = $('#contentInput' + post_id).val();


        req = $.ajax({
            url: '/updatePost',
            type: 'POST',
            data: {content: content, title: title, id: post_id}

        });

        req.done(function (data) {

            $('#roomSection' + post_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber' + post_id).text(data.post_title);

        });

    })

        //delete room
    $('.deletePostComments').on('click', function () {

        var post_id = $(this).attr('post_id');

        var r = confirm("Clear Post Comments?");

        if (r == true) {

            req = $.ajax({
                url: '/deletePostComments',
                type: 'POST',
                data: {id: post_id}

            });
            alert("Comments Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })



    $('.deleteUserFile').on('click', function () {

        var file_id = $(this).attr('file_id');

        var r = confirm("Delete File?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteUserFile',
                type: 'POST',
                data: {id: file_id}

            });
            alert("File Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })


    //delete room
    $('.deleteButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

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


            //delete room
    $('.deleteRoomComments').on('click', function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Clear Room Comments?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteRoomComments',
                type: 'POST',
                data: {id: room_id}

            });
            alert("Comments Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })

    //approve tutor
    $('.approveTutor').on('click', function () {

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
    $('.denyTutor').on('click', function () {

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
    $('.deleteUser').on('click', function () {

        var user_id = $(this).attr('user_id');
        var r = confirm("Delete User?");

        if (r == true) {


            req = $.ajax({
                url: '/deleteUser',
                type: 'POST',
                data: {id: user_id}

            });
            alert("User Deleted!")
            location.reload();
        } else {
            //nothing happens
        }

    })

    //open edit user
    $('.editUser').on('click', function () {

        var user_id = $(this).attr('user_id');

        $('.modal_editUser').show();


    })

    //close edit user
    $('.closeWindow').on('click', function () {

        var user_id = $(this).attr('user_id');

        $('.modal_editUser').hide();


    })

    //edit user
    $('.editUserForm').on('click', function () {

        var user_id = $(this).attr('user_id');

        var firstname = $('#firstName' + user_id).val();
        var lastname = $('#lastName' + user_id).val();
        var username = $('#userName' + user_id).val();
        var email = $('#email' + user_id).val();
        var role = $('#role' + user_id).val();


        req = $.ajax({
            url: '/editUser',
            type: 'POST',
            data: {firstname: firstname, lastname: lastname, username: username, id: user_id, email: email, role: role}

        });

        alert("User Edited!");
        location.reload();

    })

    //delete chat logs
    $('.deleteLogs').on('click', function () {

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
    $('.deleteRoomUploads').on('click', function () {

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

    //temp solution refresh page
    $('.refreshRoomUploads').on('click', function () {

        location.reload();


    })

    $('.deleteApplication').on('click', function () {

        var r = confirm("Re Apply?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteApplication',
                type: 'POST'

            });

            req.done(function (data) {
            window.location.reload(true);
            });

        } else {


        }

    })

    //make room private - private chat
    $('.privateButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/privateRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Private!")
        $('.privateButton').hide();
        $('.publicButton').show();



    })

    //public room - private chat
    $('.publicButton').on('click', function () {

        var room_id = $(this).attr('room_id');
        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/publicRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Public!")
        $('.publicButton').hide();
        $('.privateButton').show();


    })

    // for private profile page
    //edit user
    $('.editUserProfile').on('click', function () {

        var user_id = $(this).attr('user_id');

        var email = $('#email'+user_id).val();

        req = $.ajax({
            url: '/editUserProfile',
            type: 'POST',
            data: {email: email, id: user_id}

        });

        alert("Email Updated Successfully!");
        location.reload();

    })


     // for private profile page
    //edit user
    $('.deleteUserCourse').on('click', function () {

        var course_id = $(this).attr('course_id');

        var r = confirm("Delete Course?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteUserCourse',
                type: 'POST',
                data: {id: course_id}

            });
            alert("Course Deleted!")
            location.reload();

        } else {

            //nothing happens

        }

    })


    $('.deleteTutorCourse').on('click', function () {

        var course_id = $(this).attr('course_id');

        var r = confirm("Delete Course?");

        if (r == true) {

            req = $.ajax({
                url: '/deleteTutorCourse',
                type: 'POST',
                data: {id: course_id}

            });
            alert("Course Deleted!")
            location.reload();

        } else {

            //nothing happens

        }



    })


         // for private profile page
    //edit user
    $('.addTutorCourse').on('click', function () {

        var course_id = $(this).attr('course_id');

        var course_name = $('#tutorcourse option:selected').text();
        // var r = confirm("Delete Course?");
            req = $.ajax({
                url: '/addTutorCourse',
                type: 'POST',
                data: {course_name: course_name}

            });

            req.done(function (data) {
            window.location.reload(true);
            });


        })

        $('.clearTutorCourses').on('click', function () {

        // var r = confirm("Delete Course?");

            req = $.ajax({
                url: '/clearTutorCourses',
                type: 'POST',

            });

            req.done(function () {
            window.location.reload(true);
            });

    })


    $('.setProgram').on('click',function () {


    var program_name = $('#program_name option:selected').text();


    })

    //
    // $('.resetPosts').on('click',function () {
    //
    //         req = $.ajax({
    //             url: '/allstudentposts',
    //             type: 'POST',
    //
    //         });
    //
    //
    //
    // })


});


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


//
//
//     req = $.ajax({
//         url: '/refreshRoomUploads',
//         type: 'POST',
//         data: {name: room_name}
//
//     });
//
//     req.done(function(data) {
//
//
//
//      alert("Room Uploads Updated!!");
//     $('#file_list').fadeOut(1000).fadeIn(1000);
//
//
// });


//  alert("Room Uploads Updated!!");
// $('#file_list').fadeOut(1000).fadeIn(1000);


//
// $('.uploadRoomFile').on('click',function () {
//
//     var formData = new FormData();
//     formData.append('file', $('input[type=file]')[0].files[0]);
//
//
//     req = $.ajax({
//             url: '/uploadRoomFile',
//             type: 'POST',
//             data: {file_data: formData}
//     });
//         alert("uploaded!");
//
//
//
// })

// $('form').on('submit', function(event) {
//
// 	$.ajax({
// 		data : {
// 			name : $('#nameInput').val(),
// 			email : $('#emailInput').val()
// 		},
// 		type : 'POST',
// 		url : '/process'
// 	})
// 	.done(function(data) {
//
// 		if (data.error) {
// 			$('#errorAlert').text(data.error).show();
// 			$('#successAlert').hide();
// 		}
// 		else {
// 			$('#successAlert').text(data.name).show();
// 			$('#errorAlert').hide();
// 		}
//
// 	});
//
// 	event.preventDefault();
//
// });
//
// $('.setProgram').on('click',function () {
//
//     var program_id = $(this).attr('.program_id');
//
//         alert(program_id);
//
// })