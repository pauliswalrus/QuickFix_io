/*

QuickFix:

General js. functions file
Author: Austin Paul, Emma Hobden

Date: Nov 6.

*/

$(document).ready(function () {

//MARK : Start of Admin Portal Functions

    /*
    Admin Room management functions
    admin_room.html functions
     */

    //update room - admin
    $('.updateButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        // var name = $('#nameInput' + room_id).val();

        var title = $('#titleInput' + room_id).val();

        var content = $('#contentInput' + room_id).val();

        req = $.ajax({
            url: '/updateRoom',
            type: 'POST',
            data: {title: title, content: content, id: room_id}

        });

        req.done(function (data) {

            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber' + room_id).text(data.room_title);

        });

    });


    //delete room - admin
    $('.deleteButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

        var r = confirm("Delete Room?");

        if (r === true) {

            req = $.ajax({
                url: '/deleteRoom',
                type: 'POST',
                data: {name: name, id: room_id}

            });
            alert("Room Deleted!");
            location.reload();

        } else {
            //nothing happens
        }

    });


    //make room private - admin
    $('.privateButtonAdmin').on('click', function () {

        let room_id = $(this).attr('room_id');

        let name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/privateRoom',
            type: 'POST',
            data: {name: name, id: room_id}
        });
        alert("This Room is Private!");
        location.reload();

    });

    //make room public - admin
    $('.publicButtonAdmin').on('click', function () {

        var room_id = $(this).attr('room_id');
        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/publicRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Public!");
        location.reload();

    });


    //delete chat logs
    $('.deleteLogs').on('click', function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Delete Chat Logs?");

        if (r === true) {

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

    });

    //delete room post comments - admin
    $('.deleteRoomComments').on('click', function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Clear Room Comments?");

        if (r === true) {

            req = $.ajax({
                url: '/deleteRoomComments',
                type: 'POST',
                data: {id: room_id}

            });
            alert("Comments Deleted!");
            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);

        } else {
            //nothing happens
        }

    });


    //delete room files/uploads - admin
    $('.deleteRoomUploads').on('click', function () {

        var room_id = $(this).attr('room_id');

        var r = confirm("Delete Room Uploads?");

        if (r === true) {

            req = $.ajax({
                url: '/deleteRoomUploads',
                type: 'POST',
                data: {id: room_id}

            });
            alert("Room Uploads Cleared!");
            $('#roomSection' + room_id).fadeOut(1000).fadeIn(1000);

        } else {

        }


    });


    /*
    Admin Post management functions
    admin_posts.html functions
     */

    //update community forum post - admin
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

    });


    //delete community forum post
    $('.deletePost').on('click', function () {

        var post_id = $(this).attr('post_id');

        var r = confirm("Delete Post?");

        if (r === true) {

            req = $.ajax({
                url: '/deletePost',
                type: 'POST',
                data: {id: post_id}

            });
            alert("Post Deleted!");
            location.reload();

        } else {

            //nothing happens

        }

    });

    //delete community forum post comments - admin
    $('.deletePostComments').on('click', function () {

        var post_id = $(this).attr('post_id');

        var r = confirm("Clear Post Comments?");

        if (r === true) {

            req = $.ajax({
                url: '/deletePostComments',
                type: 'POST',
                data: {id: post_id}

            });
            alert("Comments Deleted!");
            $('#roomSection' + post_id).fadeOut(1000).fadeIn(1000);

        } else {

            //nothing happens

        }

    });


    /*
    Admin Tutor approval functions
    admin.html functions
     */

    //approve tutor - admin
    $('.approveTutor').on('click', function () {

        var user_id = $(this).attr('user_id');

        var r = confirm("Approve Tutor?");

        if (r === true) {

            req = $.ajax({
                url: '/approveTutor',
                type: 'POST',
                data: {id: user_id}

            });
            alert("Tutor Approved!");
            location.reload();

        } else {
            //nothing happens
        }

    });


    //deny tutor
    $('.denyTutor').on('click', function () {

        var user_id = $(this).attr('user_id');
        var comments = $("#appComments").val();

        var r = confirm("Deny This Tutor?");

        if (r === true) {

            req = $.ajax({
                url: '/denyTutor',
                type: 'POST',
                data: {id: user_id, comments: comments}

            });
            alert("Tutor Denied!");
            location.reload();


        } else {
            //nothing happens
        }

    });

    /*
    Admin User management functions
    all_users.html functions
     */


    //edit user - admin
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

    });

    //delete user - admin
    $('.deleteUser').on('click', function () {

        var user_id = $(this).attr('user_id');
        var r = confirm("Delete User?");

        if (r === true) {

            req = $.ajax({
                url: '/deleteUser',
                type: 'POST',
                data: {id: user_id}

            });
            alert("User Deleted!");
            location.reload();
        } else {
            //nothing happens
        }

    });

//MARK : End of Admin Portal Functions


    /*
    Delete Tutor Application functions
    check_application.html functions
     */

    $('.deleteApplication').on('click', function () {

        var r = confirm("Re Apply?");

        if (r === true) {

            req = $.ajax({
                url: '/deleteApplication',
                type: 'POST'

            });

            req.done(function (data) {
            window.location.reload(true);
            });

        } else {


        }

    });

    /*
    Chat Room functions
    private_chat.html functions
     */

    //make room private - used by tutor
    $('.privateButton').on('click', function () {

        var room_id = $(this).attr('room_id');

        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/privateRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Private!");
        $('.privateButton').hide();
        $('.publicButton').show();


    });

    //make room private - used by tutor
    $('.publicButton').on('click', function () {

        var room_id = $(this).attr('room_id');
        var name = $('#nameInput' + room_id).val();

        req = $.ajax({
            url: '/publicRoom',
            type: 'POST',
            data: {name: name, id: room_id}

        });
        alert("This Room is Public!");
        $('.publicButton').hide();
        $('.privateButton').show();

    });

    //temp solution refresh page to show updated room uploads
    $('.refreshRoomUploads').on('click', function () {

        location.reload();

    });

    /*
    Program, UserCourse and TutorCourse functions
    Used in a few html pages see comments.
    Mostly used on profile.html and userCourses.html, tutorCourses.html, etc
     */


    //sets program to filter courses by used on user profile and tutor application pages
    //used in profilePrograms.html and applicationBegin.html
    $('.setProgram').on('click',function () {

        var program_name = $('#program_name option:selected').text();

    });




});

/*

DONT NO DELETE BELOW UNSURE!


    //unsure edit user modal functions


    // //open edit user
    // $('.editUser').on('click', function () {
    //
    //     var user_id = $(this).attr('user_id');
    //
    //     $('.modal_editUser').show();
    //
    //
    // });
    //
    // //close edit user
    // $('.closeWindow').on('click', function () {
    //
    //     var user_id = $(this).attr('user_id');
    //
    //     $('.modal_editUser').hide();
    //
    //
    // });


    // //temp solution refresh page
    // $('.refreshRoomUploads').on('click', function () {
    //     location.reload();
    //
    // });



    //unsure tutor/course functions

    // $('.addTutorCourse').on('click', function () {
    //
    //     var course_id = $(this).attr('course_id');
    //
    //     var course_name = $('#tutorcourse option:selected').text();
    //     // var r = confirm("Delete Course?");
    //         req = $.ajax({
    //             url: '/addTutorCourse',
    //             type: 'POST',
    //             data: {course_name: course_name}
    //
    //         });
    //
    //         req.done(function (data) {
    //         window.location.reload(true);
    //         });
    //
    //
    // });
    //
    // $('.clearTutorCourses').on('click', function () {
    //
    //     // var r = confirm("Delete Course?");
    //
    //         req = $.ajax({
    //             url: '/clearTutorCourses',
    //             type: 'POST',
    //
    //         });
    //
    //         req.done(function () {
    //         window.location.reload(true);
    //         });
    //
    // });





*/
