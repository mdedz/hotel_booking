document.addEventListener('DOMContentLoaded', async function () {
    if (!window.flatpickr) return;

    flatpickr(".date-input", {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        allowInput: true,
        minDate: "today",
    });

    const startInput = document.querySelector("[data-range-start]");
    const endInput = document.querySelector("[data-range-end]");
    if (!startInput || !endInput) return;

    const roomId = startInput.dataset.roomId;
    if (!roomId) return;

    const yearLater = new Date();
    yearLater.setFullYear(yearLater.getFullYear() + 1);

    const endPicker = flatpickr(endInput, {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        minDate: "today",
    });

    const startPicker = flatpickr(startInput, {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        minDate: "today",
        onChange: function (selectedDates) {
            if (!selectedDates[0]) return;

            const startDate = selectedDates[0];

            endPicker.set('minDate', startDate);

            if (endPicker.selectedDates[0] &&
                disabledDates.includes(endPicker.selectedDates[0].toISOString().slice(0, 10))
            ) {
                endPicker.clear();
            }
        }
    });

    const focusable = document.querySelectorAll('.auto-focus');
    if (focusable.length) focusable[0].focus();
});
