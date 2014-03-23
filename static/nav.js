$(document).ready(function(){
  if($(".visible-phone").css("display")=="block"){
    $(".collapse").removeClass("in");
  }
  $('#menu-toggle').click(function(){
    if($(".collapse").hasClass('in'))
    {
      $(".collapse").collapse('hide');
      $(this).html('<i class="icon-chevron-down"></i>');
    }
    else 
    {
      $(".collapse").collapse('show');
      $(this).html('<i class="icon-chevron-up"></i>');
    }
  });
});