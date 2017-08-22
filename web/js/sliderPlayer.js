$(function(){
    $("#feedback").hover(function(){
        $("#feedback img").attr("src", "/imgs/feedbackHover.png");
    },function(){
        $("#feedback img").attr("src", "/imgs/feedback.png");
    });    
})