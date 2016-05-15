
$("#input_form").submit(function(e){
    
    var formData = new FormData($(this)[0]);
    // create job
    $.ajax({
        type: "POST",
        url: "/scrape_reviews",
        data: formData,
        async: true,
        success: function(data){
            alert("Your job is to run shortly with id " + data);
            // run job
            // id = data;
            // run_job(id);
        },
        cache: false,
        contentType: false,
        processData: false
    })
    e.preventDefault();
})