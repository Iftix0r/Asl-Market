/* ==========================================================================
   AslMarket.uz - Central Data Store & LocalStorage Manager
   ========================================================================== */

const STORAGE_KEYS = {
  PRODUCTS: 'aslmarket_products',
  DEBTORS: 'aslmarket_debtors',
  SALES: 'aslmarket_sales',
  SETTINGS: 'aslmarket_settings'
};

// Initial Uzbek Demo Products Dataset
const DEFAULT_PRODUCTS = [
  {
    id: 'prod_1',
    name: 'Samsung 43" Smart TV Crystal UHD',
    category: 'Elektronika',
    price: 4500000,
    costPrice: 3800000,
    stock: 8,
    barcode: '8806091234567',
    image: 'https://images.unsplash.com/photo-1593784991095-a205069470b6?auto=format&fit=crop&w=600&q=80',
    description: '4K Ultra HD smart televizor, Wi-Fi, HDR10+'
  },
  {
    id: 'prod_2',
    name: 'Artel Muzlatgich HD-345 FW',
    category: 'Maishiy Texnika',
    price: 3800000,
    costPrice: 3200000,
    stock: 5,
    barcode: '4780001239871',
    image: 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?auto=format&fit=crop&w=600&q=80',
    description: 'NoFrost tizimi, energiya tejamkor A+ sinf'
  },
  {
    id: 'prod_3',
    name: 'Nescafe Gold Qahva 190g',
    category: 'Oziq-ovqat',
    price: 85000,
    costPrice: 68000,
    stock: 45,
    barcode: '7613032123456',
    image: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80',
    description: 'Tabiiy eruvchan arabika qahvasi'
  },
  {
    id: 'prod_4',
    name: 'Ahmad Tea Grey 100g',
    category: 'Oziq-ovqat',
    price: 32000,
    costPrice: 24000,
    stock: 60,
    barcode: '5000185001234',
    image: 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80',
    description: 'Xushbuy bergamotli qora choy'
  },
  {
    id: 'prod_5',
    name: 'Coca-Cola Zero 1.5L (12 dona)',
    category: 'Ichimliklar',
    price: 132000,
    costPrice: 108000,
    stock: 25,
    barcode: '5449000000996',
    image: 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=600&q=80',
    description: 'Shakarsiz salqinlashtiruvchi ichimlik'
  },
  {
    id: 'prod_6',
    name: 'Ariel Avtomat Kir Yuvish Kukuni 3kg',
    category: "Ro'zg'or buyumlari",
    price: 75000,
    costPrice: 60000,
    stock: 3, // Low stock demo!
    barcode: '8001090123456',
    image: 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=600&q=80',
    description: 'Dog\'larni samarali ketkazuvchi kir kukuni'
  }
];

// Helper to construct timestamps X days/hours ago
const hoursAgo = (h) => new Date(Date.now() - h * 3600 * 1000).toISOString();
const daysAgo = (d) => new Date(Date.now() - d * 24 * 3600 * 1000).toISOString();

// Initial Debtors Dataset with varied elapsed times for demoing "Qancha vaqt o'tgan"
const DEFAULT_DEBTORS = [
  {
    id: 'debt_1',
    name: 'Alisher Qodirov',
    phone: '+998 90 123 45 67',
    amount: 1450000,
    initialAmount: 1450000,
    createdAt: daysAgo(3), // 3 days ago -> Normal status
    dueDate: daysAgo(-10), // due in 10 days
    status: 'active',
    items: 'Artel Muzlatgich uchun bo\'nak, qolgan qarz',
    payments: []
  },
  {
    id: 'debt_2',
    name: 'Jahongir Rahimov',
    phone: '+998 93 987 65 43',
    amount: 520000,
    initialAmount: 850000,
    createdAt: daysAgo(14), // 14 days ago -> Warning status
    dueDate: daysAgo(2),
    status: 'active',
    items: 'Nescafe qahvalari va xaridlar',
    payments: [
      { date: daysAgo(5), amount: 330000, note: 'Naqd to\'lov qilindi' }
    ]
  },
  {
    id: 'debt_3',
    name: 'Sardorbek Umarov',
    phone: '+998 97 555 12 34',
    amount: 2800000,
    initialAmount: 2800000,
    createdAt: daysAgo(42), // 42 days ago -> URGENT / Kechikkan status (pulsing red)
    dueDate: daysAgo(12),
    status: 'active',
    items: 'Samsung Smart TV (Nasiya sotuv)',
    payments: []
  },
  {
    id: 'debt_4',
    name: 'Malika Axmedova',
    phone: '+998 91 333 44 55',
    amount: 0,
    initialAmount: 450000,
    createdAt: daysAgo(20),
    dueDate: daysAgo(5),
    status: 'paid',
    items: 'Ariel kukunlari va ro\'zg\'or mollari',
    payments: [
      { date: daysAgo(2), amount: 450000, note: 'To\'liq yopildi (Karta)' }
    ]
  }
];

// Initial Sales Dataset
const DEFAULT_SALES = [
  {
    id: 'sale_101',
    date: daysAgo(1),
    customerName: 'Xaridor (Naqd)',
    totalAmount: 4500000,
    paymentMethod: 'Naqd',
    itemsCount: 1
  },
  {
    id: 'sale_102',
    date: daysAgo(2),
    customerName: 'Jahongir Rahimov',
    totalAmount: 850000,
    paymentMethod: 'Nasiya',
    itemsCount: 3
  }
];

export class Store {
  constructor() {
    this.init();
  }

  init() {
    if (!localStorage.getItem(STORAGE_KEYS.PRODUCTS)) {
      localStorage.setItem(STORAGE_KEYS.PRODUCTS, JSON.stringify(DEFAULT_PRODUCTS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.DEBTORS)) {
      localStorage.setItem(STORAGE_KEYS.DEBTORS, JSON.stringify(DEFAULT_DEBTORS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.SALES)) {
      localStorage.setItem(STORAGE_KEYS.SALES, JSON.stringify(DEFAULT_SALES));
    }
  }

  // --- PRODUCTS API ---
  getProducts() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.PRODUCTS) || '[]');
  }

  saveProducts(products) {
    localStorage.setItem(STORAGE_KEYS.PRODUCTS, JSON.stringify(products));
  }

  addProduct(product) {
    const products = this.getProducts();
    product.id = 'prod_' + Date.now();
    products.unshift(product);
    this.saveProducts(products);
    return product;
  }

  updateProduct(updatedProduct) {
    let products = this.getProducts();
    products = products.map(p => p.id === updatedProduct.id ? updatedProduct : p);
    this.saveProducts(products);
  }

  deleteProduct(id) {
    let products = this.getProducts();
    products = products.filter(p => p.id !== id);
    this.saveProducts(products);
  }

  // --- DEBTORS API (Qarzdorlar Daftari) ---
  getDebtors() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.DEBTORS) || '[]');
  }

  saveDebtors(debtors) {
    localStorage.setItem(STORAGE_KEYS.DEBTORS, JSON.stringify(debtors));
  }

  addDebtor(debtor) {
    const debtors = this.getDebtors();
    debtor.id = 'debt_' + Date.now();
    debtor.createdAt = debtor.createdAt || new Date().toISOString();
    debtor.status = debtor.amount > 0 ? 'active' : 'paid';
    debtor.payments = debtor.payments || [];
    debtors.unshift(debtor);
    this.saveDebtors(debtors);
    return debtor;
  }

  recordDebtPayment(debtorId, paymentAmount, paymentNote = '') {
    const debtors = this.getDebtors();
    const debtor = debtors.find(d => d.id === debtorId);
    if (!debtor) return false;

    const pay = parseFloat(paymentAmount);
    debtor.amount = Math.max(0, debtor.amount - pay);
    debtor.payments.push({
      date: new Date().toISOString(),
      amount: pay,
      note: paymentNote
    });

    if (debtor.amount === 0) {
      debtor.status = 'paid';
    }

    this.saveDebtors(debtors);
    return debtor;
  }

  // --- SALES API ---
  getSales() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.SALES) || '[]');
  }

  addSale(saleData) {
    const sales = this.getSales();
    saleData.id = 'sale_' + Date.now();
    saleData.date = new Date().toISOString();
    sales.unshift(saleData);
    localStorage.setItem(STORAGE_KEYS.SALES, JSON.stringify(sales));

    // Deduct inventory
    if (saleData.items && Array.isArray(saleData.items)) {
      const products = this.getProducts();
      saleData.items.forEach(item => {
        const prod = products.find(p => p.id === item.productId);
        if (prod) {
          prod.stock = Math.max(0, prod.stock - item.qty);
        }
      });
      this.saveProducts(products);
    }

    return saleData;
  }

  // Helper formatting for UZS currency
  static formatMoney(amount) {
    return new Intl.NumberFormat('uz-UZ').format(amount || 0) + " so'm";
  }
}

export const store = new Store();
