document.addEventListener('DOMContentLoaded', async function () {
    if (!window.flatpickr) return;

    // single date pickers
    flatpickr(".date-input", {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        allowInput: true,
        minDate: "today",
    });

    const startInput = document.querySelector("[data-range-start]");
    const endInput   = document.querySelector("[data-range-end]");
    if (!startInput || !endInput) return;

    const roomId = startInput.dataset.roomId;
    if (!roomId) return;

    // Load availability
    const today = new Date().toISOString().slice(0, 10);
    const yearLater = new Date();
    yearLater.setFullYear(yearLater.getFullYear() + 1);
    const until = yearLater.toISOString().slice(0, 10);

    const res = await fetch(
        `/api/rooms/${roomId}/availability/?start_date=${today}&end_date=${until}`
    );
    const data = await res.json();
    const disabledDates = data.disabled_dates || [];

    // Start picker
    const startPicker = flatpickr(startInput, {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        minDate: "today",
        disable: disabledDates,
        onChange: function (selectedDates) {
            if (!selectedDates[0]) return;

            const startDate = selectedDates[0];
            endPicker.set('minDate', startDate);

            // If end is disabled - drop it
            if (
                endPicker.selectedDates[0] &&
                disabledDates.includes(
                endPicker.selectedDates[0].toISOString().slice(0, 10)
                )
            ) {
                endPicker.clear();
            }
        }
    });

    // End picker
    const endPicker = flatpickr(endInput, {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        minDate: "today",
        disable: disabledDates,
    });

    // UX micro fix
    const focusable = document.querySelectorAll('.auto-focus');
    if (focusable.length) focusable[0].focus();
});
