/**
 * AslFood Mobile API Service
 * Django backend bilan barcha muloqot shu fayldan o'tadi.
 *
 * BASE_URL ni o'zingizning server IP manziliga o'zgartiring.
 * Masalan: 'http://192.168.1.100:8000'  (local Wi-Fi)
 *          'https://aslmarket.uz'         (production)
 */

export const BASE_URL = 'http://192.168.1.100:8000';

const API = `${BASE_URL}/api/food`;

// ─── Umumiy so'rov yordamchisi ───────────────────────────────────────────────

async function request(path, options = {}) {
  const url = `${API}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };
  try {
    const response = await fetch(url, config);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`API xatolik [${path}]:`, error);
    return { success: false, error: 'Server bilan aloqa yo\'g\'i. Internet yoki server manzilini tekshiring.' };
  }
}

// ─── MENYU ──────────────────────────────────────────────────────────────────

/** Mavjud taomlarni kategoriyalar bilan olish (mijoz uchun) */
export const getMenu = () => request('/menu/');

/** Barcha taomlar (admin panel uchun — mavjud bo'lmagan ham) */
export const getAllMenuItems = () => request('/menu/all/');

/** Kategoriyalar ro'yxati */
export const getCategories = () => request('/categories/');

/** Taom mavjud/tugagan toggle */
export const toggleFoodItem = (id) =>
  request(`/menu/toggle/${id}/`, { method: 'POST' });

/** Yangi taom qo'shish */
export const addFoodItem = (itemData) =>
  request('/menu/add/', {
    method: 'POST',
    body: JSON.stringify(itemData),
  });

/** Taomni tahrirlash */
export const editFoodItem = (id, itemData) =>
  request(`/menu/edit/${id}/`, {
    method: 'POST',
    body: JSON.stringify(itemData),
  });

/** Taomni o'chirish */
export const deleteFoodItem = (id) =>
  request(`/menu/delete/${id}/`, { method: 'POST' });

// ─── BUYURTMALAR ─────────────────────────────────────────────────────────────

/**
 * Buyurtmalar ro'yxatini olish
 * @param {string} status - 'new' | 'preparing' | 'delivering' | 'completed' | '' (barchasi)
 */
export const getOrders = (status = '') => {
  const query = status ? `?status=${status}` : '';
  return request(`/orders/${query}`);
};

/** Bitta buyurtma tafsilotlari */
export const getOrderDetail = (id) => request(`/orders/${id}/`);

/** Buyurtma holatini yangilash (oshpaz paneli uchun) */
export const updateOrderStatus = (orderId, newStatus) =>
  request('/orders/status/', {
    method: 'POST',
    body: JSON.stringify({ order_id: orderId, new_status: newStatus }),
  });

/** Yangi buyurtma berish (mijoz uchun) */
export const placeOrder = (orderData) =>
  request('/orders/place/', {
    method: 'POST',
    body: JSON.stringify(orderData),
  });

/**
 * Buyurtma kodi orqali holat kuzatish
 * @param {string} code - masalan 'FOOD-AB12CD'
 */
export const trackOrder = (code) =>
  request(`/orders/track/${code}/`);

// ─── STATISTIKA ──────────────────────────────────────────────────────────────

/** Kunlik/haftalik/umumiy daromad va buyurtmalar statistikasi */
export const getStats = () => request('/stats/');
