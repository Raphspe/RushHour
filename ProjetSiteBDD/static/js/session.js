 // Affiche les images du dataset
 var URL = "http://slhdg001.maif.local:9876/"
 function predInit(session_id) {
    var BaseImgUrl = "http://slhdg001.maif.local:8896/images/";
    $.ajax({
        url: URL + "data?session_id=" + session_id,
        method: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            // if (xhr.status == 204) {
            //     $("#counter-container").hide();
            //     $("#msg-container").hide();
            //     $("#yes-no-container").hide();
            //     $("#msg-no-more-result-container").show();
            // }
            // if (xhr.status == 200) {
            //     $("#yes-no-container").show();
            //     $("#counter-container").show();
            //     $("#msg-container").show();
            //     $("#msg-no-more-result-container").hide();

            //     // We inject data to the UI
            //     $('#id').val(data.id);
            //     $("#main-img").attr("src", BaseImgUrl + "1/Appenzeller-n02107908_933.jpg");
            //     //$("#classe").val(data.supervisor.session);
            //     //$('#second_class').text(data.second_class);

            // }
            $('#id').val(data.id);
            $("#main-img").attr("src", BaseImgUrl + "/Appenzeller-n02107908_933.jpg");
        },
        error: function (xhr, ajaxOptions, thrownError) {
            switch (xhr.status) {
                case 500:
                    alert("Internal server error");

            }
        }
    })
}

$(document).ready(function () {
    var sessionId = $("#id_session").val();
    predInit(sessionId);
    
});