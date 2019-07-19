$(document).ready(function () {

  $('td.cellule').click(function (e) {
    const self = $(this)
    const l1 = $(self.children('div .line1'));
    const l2 = $(self.children('div .line2'));
    const checkBox = $(self.children('input[type=checkbox]'));


    if (self.hasClass('unselectable')) {
      console.log("penis")
      e.preventDefault();
      return false;
    }
    if (l1.hasClass('active')) {
      checkBox.prop('checked', false); // Checks it
      l1.removeClass('active');
      l2.removeClass('active');
    } else {
      checkBox.prop('checked', true); // Checks it
      l1.addClass('active');
      l2.addClass('active');
    }
  });


});
