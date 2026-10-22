// Небольшое улучшение формы. Сервер повторно проверяет даты и доступность.
const bookingForm = document.getElementById('booking-form');
if (bookingForm) {
  const room = bookingForm.elements.room_id;
  const start = bookingForm.elements.check_in;
  const end = bookingForm.elements.check_out;
  function updateEstimate() {
    const nights = (Date.parse(end.value) - Date.parse(start.value)) / 86400000;
    const price = Number(room.selectedOptions[0]?.dataset.price);
    const valid = Number.isFinite(nights) && nights > 0;
    end.setCustomValidity(end.value && start.value && !valid ? 'Выезд должен быть позже заезда' : '');
    const total = document.getElementById('booking-total');
    total.textContent = valid && Number.isFinite(price)
      ? new Intl.NumberFormat('ru-RU', {maximumFractionDigits: 2}).format(nights * price) + ' TJS'
      : 'Выберите номер и даты';
    document.getElementById('booking-nights').textContent = valid && Number.isFinite(price)
      ? 'Ночей: ' + nights + ' · Тариф: ' + price + ' TJS / ночь. Без дополнительных услуг.'
      : 'Количество ночей × текущая цена за ночь. Без дополнительных услуг.';
  }
  bookingForm.addEventListener('input', updateEstimate);
  bookingForm.addEventListener('change', updateEstimate);
  updateEstimate();
}
