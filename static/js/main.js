$(document).ready(() => {
  maxDateIsToday();
});

function maxDateIsToday() {
  console.log(new Date().toISOString().split("T")[0]);
  
  $(".js-valid-date-input").attr("max", new Date().toISOString().split("T")[0]);
}