var collapseOrShow = function(){
  if($(".visible-phone").css("display")=="block")
  {$(".collapse").collapse('hide');}
  else 
  {$(".collapse").collapse('show');}
}
$(window).resize(function(){ 
  collapseOrShow();
});
$(document).ready(function(){
  if($(".visible-phone").css("display")=="block"){
    $(".collapse").removeClass("in");
  }
});