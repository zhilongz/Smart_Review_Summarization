function renderResult(d,tStatus, jqxhr){
    $("#progress")[0].innerHTML = "Done! Please check your results below.";
    product_id = d;
    var resultUrl = "/srs_result_box_bokeh/" + product_id;

    $("#resultLink")[0].href = resultUrl;
    $("#resultLink")[0].innerHTML = product_id+" srs result";

}

function linspace(a,b,n) {
    if(typeof n === "undefined") n = Math.max(Math.round(b-a)+1,1);
    if(n<2) { return n===1?[a]:[]; }
    var i,ret = Array(n);
    n--;
    for(i=n;i>=0;i--) { ret[i] = (i*b+(n-i)*a)/n; }
    return ret;
}

function fillHistData(cb_data, histPlot_data, features, hist_data) {

    var current_index = cb_data.index['1d'].indices[0];

    if (typeof current_index != 'undefined'){

        histTop = hist_data['tops'][current_index];
        histLeft = hist_data['lefts'][current_index];
        histRight = hist_data['rights'][current_index];
        feature = features[current_index];

        bin_num = histTop.length;
        //Defining the drawing parameters for Fig2
        histPlot_data['bottom'] = new Array(bin_num).fill(0);
        histPlot_data['top'] = histTop;
        histPlot_data['left']= histLeft;
        histPlot_data['right']= histRight;
        histPlot_data['feature'] = feature;

        console.log(histPlot_data['feature']);
        $("#histPlotTitle p").text(histPlot_data['feature']);           
        }
    
}

function fillSampleReviews(cb_data, sampleSentences_dict, feature) {
    var barIdx = cb_data.index['1d'].indices[0];

    if (typeof barIdx != 'undefined'){
        var example_sen = sampleSentences_dict[feature][barIdx];
        console.log(example_sen[0]);
        $("#sample_sen1").text(example_sen[0]);
    }
    else {
        $("#sample_sen1").text("");
    }
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