$(document).ready(function () {
  console.log("jQuery is working!");
  $(".menu-button").click(function () {
    $(".menu").toggleClass("show");
  });

  $(window).resize(function () {
    if ($(window).width() > 768) {
      $(".menu").removeClass("show");
    }
  });
});
