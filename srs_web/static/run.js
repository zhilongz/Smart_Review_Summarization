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

function fillHistData(cb_data, fig2data, features, all_score_list) {

    var current_index = cb_data.index['1d'].indices[0];

    if (typeof current_index != 'undefined'){

        //fill s2 with data needed for histogram
        var selected_list=all_score_list[current_index];
        var min = Math.min(...selected_list);
        var max = Math.max(...selected_list);
        var score_num = selected_list.length;
        var bin_num = 4;
        if(score_num<=10){ bin_num = 2;} 
        else if (10 < score_num && score_num <= 30) { bin_num = 3;}
        else if (30 <score_num && score_num <= 100) { bin_num = 4;}
        else if (score_num > 100){bin_num = 5;
        }
        var hist = new Array(bin_num).fill(0);
        var delimiter = linspace (min, max, bin_num+1);
        for (i = 0; i < score_num; i++){
            score = selected_list[i];
            for (j = 0; j < bin_num; j++){
                if(delimiter[j] <= score && score < delimiter[j+1]){
                    hist[j]++;
                }
            }
        }
        //Defining the drawing parameters for Fig2
        fig2data['bottom'] = new Array(bin_num).fill(0);
        fig2data['top'] = hist;
        fig2data['left']= delimiter.slice(0,bin_num);
        fig2data['right']= delimiter.slice(1,bin_num+1);
        
        fig2data['feature'] = features[current_index];
        console.log(fig2data['feature']);    
        
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