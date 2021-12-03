/* Resizing textareas
code from https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize */

jQuery.fn.extend({
  autoHeight: function () {
    function autoHeight_(element) {
      return jQuery(element)
        .css({ "height": "35px", "overflow-y": "hidden" })
        .height(element.scrollHeight);
    }
    return this.each(function() {
      autoHeight_(this).on("input", function() {
        autoHeight_(this);
      });
    });
  }
});