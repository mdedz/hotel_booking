document.addEventListener('DOMContentLoaded', function () {
  // flatpickr initialization for elements with .date-input
  if (window.flatpickr) {
    // single date pickers (login/profile etc)
    flatpickr(".date-input", {
      dateFormat: "Y-m-d",
      altInput: true,
      altFormat: "F j, Y",
      allowInput: true,
      minDate: "today",
      ariaDateFormat: "Y-m-d"
    });

    // range pickers: inputs with data-range-start / data-range-end
    const start = document.querySelector("[data-range-start]");
    const end = document.querySelector("[data-range-end]");
    if (start && end) {
      const startPicker = flatpickr(start, {
        dateFormat: "Y-m-d",
        altInput: true, altFormat: "F j, Y",
        minDate: "today",
        onChange: function(selectedDates, dateStr){
          if (selectedDates[0]) {
            endPicker.set('minDate', selectedDates[0]);
            // if end earlier than start -> clear end
            if (endPicker.selectedDates[0] && endPicker.selectedDates[0] <= selectedDates[0]) {
              endPicker.clear();
            }
          }
        }
      });
      const endPicker = flatpickr(end, {
        dateFormat: "Y-m-d",
        altInput: true, altFormat: "F j, Y",
        minDate: "today"
      });
    }
  }

  // small enhancement: auto-focus first input in modal forms
  const focusable = document.querySelectorAll('.auto-focus');
  if (focusable.length) focusable[0].focus();
});
