function renderResult(d,tStatus, jqxhr){
    $("#progress")[0].innerHTML = "Done! Please check your results below.";
    product_id = d;
    var resultUrl = "/srs_result_box_bokeh/" + product_id;

    $("#resultLink")[0].href = resultUrl;
    $("#resultLink")[0].innerHTML = product_id+" srs result";

}

$("#input_form").submit(function(e){    
    var formData = new FormData($(this)[0]);
    // create job
    $.ajax({
        type: "POST",
        url: "/scrape_reviews",
        data: formData,
        async: true,
        success: function(data){
            alert("Your summarization for " + data + " is ready!");
            // run job
            id = data;
            renderResult(id);
        },
        cache: false,
        contentType: false,
        processData: false
    })
    e.preventDefault();
})

$(document).ready(function(){
    $("#addInput2").click(function(e){
        $("#input2").show();
        var Summarize_Button = document.getElementById('Summarize');
        Summarize_Button.value= 'Compare';      
        $("main_section").css({"padding-bottom": "10px"});
        e.preventDefault();
    });
    $("#hideInput2").click(function(e){
        $("#input2").hide();
        var Summarize_Button = document.getElementById('Summarize');
        Summarize_Button.value= 'Summarize';
        e.preventDefault();
    });    
});