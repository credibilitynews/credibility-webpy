var collapseOrShow = function(){
  if($(".visible-phone").css("display")=="block")
  {$(".collapse").removeClass('in');}
  else 
  {$(".collapse").addClass('in');}
}
$(document).ready(function(){
  if($(".visible-phone").css("display")=="block"){
    $(".collapse").removeClass("in");
  }
  $('#menu-toggle').click(function(){
    if($(".collapse").hasClass('in'))
    {
      $(".collapse").removeClass('in');
      $(this).html('<i class="icon-chevron-down"></i>');
    }
    else 
    {
      $(".collapse").addClass('in');
      $(this).html('<i class="icon-chevron-up"></i>');
    }
  });
});