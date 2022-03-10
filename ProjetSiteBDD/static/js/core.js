$(document).ready(function () {
    var sessionId = $("#id_session").val();
    $(document).on("click", ".deleteclass", function () {
        var classe = $(this).attr("id");
        var url = 'http://slhdg001.maif.local:9876/delete-class';
        var postData = { session_id: sessionId, classe_id: classe };
        $.post(url, postData, function (data, status) {
            $("#" + classe).remove();
            console.log("Accept request done");
        });
    });
});
$("#add_class").on("click", function () {
    var classe = $("#classe_field").val();
    if (classe == '' || classe == ' ') {
        alert('Nom de classe invalide');
        return null
    }
    var id = $("#id_session").val();
    var url = 'http://slhdg001.maif.local:9876/add-class';
    var postData = { classe: classe, id: id };
    // jQuery .post method is used to send post request.
    $.post(url, postData, function (data, status) {
        $("#list-container").append("<br><a class='waves-light btn grey darken-2 deleteclass' name='" + classe + "' \
            id='"+ classe + "'>" + classe + "<i class='material-icons right'>delete_forever</i></a><br>");
        console.log("Accept request done")
    });
    // var settings = {
    //     "url": "http://slhdg001.maif.local:9876/add-class",
    //     "method": "POST",
    //     "headers": {
    //         "Content-Type": "application/json"
    //     },
    //     "data": { 
    //         JSON.stringify({'classe': classe})
    //     }
    // };
    // $.ajax(settings).done(function (response) {

    // });
});