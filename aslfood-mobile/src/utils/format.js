/**
 * AslFood — Foydali formatlash funksiyalari
 */

/** Narxni o'zbekcha formatda ko'rsatish: 32000 → "32 000 so'm" */
export function formatPrice(amount) {
  if (amount == null) return "0 so'm";
  return new Intl.NumberFormat('uz-UZ').format(amount) + " so'm";
}

/** Sanani o'qilishi oson formatda: "2026-08-22 14:30" → "22.08.2026 14:30" */
export function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr.replace(' ', 'T'));
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hour = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${day}.${month}.${year} ${hour}:${min}`;
}

/** Faqat vaqt: "14:30" */
export function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr.replace(' ', 'T'));
  const hour = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${hour}:${min}`;
}

/** Necha daqiqa oldin: "5 daqiqa oldin", "2 soat oldin" */
export function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr.replace(' ', 'T'));
  const now = new Date();
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Hozir';
  if (diffMins < 60) return `${diffMins} daqiqa oldin`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} soat oldin`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} kun oldin`;
}

/** Buyurtma turini uzbekcha chiqarish */
export function orderTypeLabel(type) {
  switch (type) {
    case 'delivery': return '🛵 Dostavka';
    case 'pickup': return '🛍️ Olib ketish';
    case 'table': return '🍽️ Zalda';
    default: return type;
  }
}
