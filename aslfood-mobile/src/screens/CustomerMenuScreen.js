/**
 * CustomerMenuScreen — Mijoz uchun menyu va savat
 *
 * - Kategoriyalar bo'yicha filtrlash
 * - Taom kartalar gridi
 * - Pastki savat paneli (float)
 * - Buyurtma berish modal formasi
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  SafeAreaView, StatusBar, Image, Modal, TextInput,
  ScrollView, Alert, ActivityIndicator, KeyboardAvoidingView,
  Platform, Animated,
} from 'react-native';

import { getMenu, placeOrder } from '../services/api';
import { Colors } from '../utils/colors';
import { formatPrice, orderTypeLabel } from '../utils/format';

const ORDER_TYPES = [
  { key: 'delivery', label: '🛵 Dostavka' },
  { key: 'pickup',   label: '🛍️ Olib ketish' },
  { key: 'table',    label: '🍽️ Zalda' },
];

export default function CustomerMenuScreen({ navigation }) {
  const [categories,    setCategories]    = useState([]);
  const [allItems,      setAllItems]      = useState([]);
  const [selectedCat,   setSelectedCat]   = useState(null); // null = barchasi
  const [cart,          setCart]          = useState([]);
  const [loading,       setLoading]       = useState(true);
  const [cartVisible,   setCartVisible]   = useState(false);
  const [placing,       setPlacing]       = useState(false);

  // Buyurtma formasi
  const [customerName,  setCustomerName]  = useState('');
  const [phone,         setPhone]         = useState('');
  const [address,       setAddress]       = useState('');
  const [orderType,     setOrderType]     = useState('delivery');

  // Savat tugmasi animatsiyasi
  const scaleAnim = useRef(new Animated.Value(1)).current;

  // ─── Ma'lumot yuklash ────────────────────────────────────────────────────

  const fetchMenu = useCallback(async () => {
    setLoading(true);
    const res = await getMenu();
    if (res.success) {
      setCategories(res.categories);
      const items = res.categories.flatMap(cat =>
        cat.items.map(item => ({ ...item, categoryName: cat.name }))
      );
      setAllItems(items);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchMenu(); }, [fetchMenu]);

  // ─── Filtrlangan taomlar ─────────────────────────────────────────────────

  const displayItems = selectedCat
    ? allItems.filter(item => {
        const cat = categories.find(c => c.id === selectedCat);
        return cat?.items.some(i => i.id === item.id);
      })
    : allItems;

  // ─── Savat amallari ──────────────────────────────────────────────────────

  const cartTotal    = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const cartCount    = cart.reduce((sum, i) => sum + i.qty, 0);

  const pulseCart = () => {
    Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 1.2, duration: 120, useNativeDriver: true }),
      Animated.timing(scaleAnim, { toValue: 1,   duration: 120, useNativeDriver: true }),
    ]).start();
  };

  const addToCart = (item) => {
    setCart(prev => {
      const existing = prev.find(i => i.id === item.id);
      if (existing) return prev.map(i => i.id === item.id ? { ...i, qty: i.qty + 1 } : i);
      return [...prev, { id: item.id, name: item.name, price: item.price, qty: 1 }];
    });
    pulseCart();
  };

  const removeFromCart = (itemId) => {
    setCart(prev => {
      const existing = prev.find(i => i.id === itemId);
      if (!existing) return prev;
      if (existing.qty === 1) return prev.filter(i => i.id !== itemId);
      return prev.map(i => i.id === itemId ? { ...i, qty: i.qty - 1 } : i);
    });
  };

  const getQty = (itemId) => cart.find(i => i.id === itemId)?.qty || 0;

  const clearCart = () => setCart([]);

  // ─── Buyurtma berish ─────────────────────────────────────────────────────

  const handlePlaceOrder = async () => {
    if (cart.length === 0) {
      Alert.alert('Savat bo\'sh', 'Iltimos taom tanlang'); return;
    }
    if (!customerName.trim()) {
      Alert.alert('Xatolik', 'Ismingizni kiriting'); return;
    }
    if (!phone.trim()) {
      Alert.alert('Xatolik', 'Telefon raqamingizni kiriting'); return;
    }

    setPlacing(true);
    const res = await placeOrder({
      cart: cart.map(i => ({ id: i.id, qty: i.qty })),
      customer_name: customerName.trim(),
      phone: phone.trim(),
      address: address.trim(),
      order_type: orderType,
    });
    setPlacing(false);

    if (res.success) {
      setCartVisible(false);
      clearCart();
      Alert.alert(
        '🎉 Buyurtma qabul qilindi!',
        `Buyurtma kodingiz: #${res.order_code}\n\nHolat kuzatish uchun "Kuzatish" bo'limiga o'ting.`,
        [
          {
            text: 'Holat kuzatish',
            onPress: () => navigation.navigate('TrackOrder', { orderCode: res.order_code }),
          },
          { text: 'OK', style: 'cancel' },
        ]
      );
    } else {
      Alert.alert('Xatolik', res.error || 'Buyurtma berishda xatolik');
    }
  };

  // ─── Render ──────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.primaryLight} />
        <Text style={styles.loadingText}>Menyu yuklanmoqda...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>🍔 AslFood Menyu</Text>
          <Text style={styles.headerSub}>{allItems.length} ta taom mavjud</Text>
        </View>
      </View>

      {/* Kategoriya filtri */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.catRow}
      >
        <TouchableOpacity
          style={[styles.catChip, !selectedCat && styles.catChipActive]}
          onPress={() => setSelectedCat(null)}
        >
          <Text style={[styles.catChipText, !selectedCat && styles.catChipTextActive]}>
            Barchasi
          </Text>
        </TouchableOpacity>
        {categories.map(cat => (
          <TouchableOpacity
            key={cat.id}
            style={[styles.catChip, selectedCat === cat.id && styles.catChipActive]}
            onPress={() => setSelectedCat(cat.id)}
          >
            <Text style={[styles.catChipText, selectedCat === cat.id && styles.catChipTextActive]}>
              {cat.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Taomlar ro'yxati */}
      <FlatList
        data={displayItems}
        keyExtractor={item => String(item.id)}
        numColumns={2}
        contentContainerStyle={styles.grid}
        columnWrapperStyle={styles.gridRow}
        renderItem={({ item }) => (
          <FoodCard
            item={item}
            qty={getQty(item.id)}
            onAdd={() => addToCart(item)}
            onRemove={() => removeFromCart(item.id)}
          />
        )}
        ListEmptyComponent={
          <View style={styles.emptyWrap}>
            <Text style={styles.emptyEmoji}>🍽️</Text>
            <Text style={styles.emptyText}>Bu kategoriyada taom yo'q</Text>
          </View>
        }
        // Savat tugmasi uchun pastdan bo'shliq
        contentInset={{ bottom: 90 }}
        ListFooterComponent={<View style={{ height: 100 }} />}
      />

      {/* Float savat tugmasi */}
      {cartCount > 0 && (
        <Animated.View style={[styles.cartFloatWrap, { transform: [{ scale: scaleAnim }] }]}>
          <TouchableOpacity
            style={styles.cartFloatBtn}
            onPress={() => setCartVisible(true)}
            activeOpacity={0.9}
          >
            <Text style={styles.cartFloatEmoji}>🛍️</Text>
            <Text style={styles.cartFloatLabel}>
              Savat — {cartCount} ta taom
            </Text>
            <Text style={styles.cartFloatTotal}>{formatPrice(cartTotal)}</Text>
          </TouchableOpacity>
        </Animated.View>
      )}

      {/* Buyurtma modal */}
      <Modal
        visible={cartVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setCartVisible(false)}
      >
        <KeyboardAvoidingView
          style={styles.modalOverlay}
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
          <View style={styles.modalCard}>
            {/* Modal header */}
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>🛍️ Buyurtmani Tasdiqlash</Text>
              <TouchableOpacity onPress={() => setCartVisible(false)}>
                <Text style={styles.modalCloseBtn}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Savat elementlari */}
              {cart.map(item => (
                <View key={item.id} style={styles.cartItem}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.cartItemName}>{item.name}</Text>
                    <Text style={styles.cartItemPrice}>{formatPrice(item.price)} × {item.qty}</Text>
                  </View>
                  <View style={styles.qtyRow}>
                    <TouchableOpacity
                      style={styles.qtyBtn}
                      onPress={() => removeFromCart(item.id)}
                    >
                      <Text style={styles.qtyBtnText}>−</Text>
                    </TouchableOpacity>
                    <Text style={styles.qtyVal}>{item.qty}</Text>
                    <TouchableOpacity
                      style={styles.qtyBtn}
                      onPress={() => addToCart(item)}
                    >
                      <Text style={styles.qtyBtnText}>+</Text>
                    </TouchableOpacity>
                  </View>
                  <Text style={styles.cartItemTotal}>
                    {formatPrice(item.price * item.qty)}
                  </Text>
                </View>
              ))}

              {/* Jami */}
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Jami:</Text>
                <Text style={styles.totalValue}>{formatPrice(cartTotal)}</Text>
              </View>

              {/* Buyurtma turi */}
              <Text style={styles.formLabel}>Buyurtma turi</Text>
              <View style={styles.orderTypeRow}>
                {ORDER_TYPES.map(type => (
                  <TouchableOpacity
                    key={type.key}
                    style={[
                      styles.orderTypeBtn,
                      orderType === type.key && styles.orderTypeBtnActive,
                    ]}
                    onPress={() => setOrderType(type.key)}
                  >
                    <Text style={[
                      styles.orderTypeBtnText,
                      orderType === type.key && styles.orderTypeBtnTextActive,
                    ]}>
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Forma */}
              <Text style={styles.formLabel}>Ismingiz *</Text>
              <TextInput
                style={styles.input}
                placeholder="To'liq ismingiz..."
                placeholderTextColor={Colors.textDim}
                value={customerName}
                onChangeText={setCustomerName}
              />

              <Text style={styles.formLabel}>Telefon *</Text>
              <TextInput
                style={styles.input}
                placeholder="+998 90 123 45 67"
                placeholderTextColor={Colors.textDim}
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
              />

              {orderType === 'delivery' && (
                <>
                  <Text style={styles.formLabel}>Yetkazish manzili</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Toshkent, Yunusobod 4-mavze..."
                    placeholderTextColor={Colors.textDim}
                    value={address}
                    onChangeText={setAddress}
                  />
                </>
              )}

              {orderType === 'table' && (
                <>
                  <Text style={styles.formLabel}>Stol raqami</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Masalan: Stol #5"
                    placeholderTextColor={Colors.textDim}
                    value={address}
                    onChangeText={setAddress}
                  />
                </>
              )}

              {/* Buyurtma tugmasi */}
              <TouchableOpacity
                style={[styles.submitBtn, placing && { opacity: 0.7 }]}
                onPress={handlePlaceOrder}
                disabled={placing}
              >
                {placing ? (
                  <ActivityIndicator color={Colors.bgDark} />
                ) : (
                  <Text style={styles.submitBtnText}>
                    ✅ Buyurtma Berish — {formatPrice(cartTotal)}
                  </Text>
                )}
              </TouchableOpacity>

              <View style={{ height: 24 }} />
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

// ─── FoodCard komponenti ──────────────────────────────────────────────────────

function FoodCard({ item, qty, onAdd, onRemove }) {
  return (
    <View style={fcStyles.card}>
      <Image
        source={{ uri: item.image_url || 'https://via.placeholder.com/160' }}
        style={fcStyles.image}
        resizeMode="cover"
      />
      <View style={fcStyles.body}>
        <Text style={fcStyles.name} numberOfLines={2}>{item.name}</Text>
        <Text style={fcStyles.category}>{item.categoryName}</Text>
        <Text style={fcStyles.prepTime}>⏱ ~{item.preparation_time_mins} daq</Text>
        <Text style={fcStyles.price}>{formatPrice(item.price)}</Text>

        {qty === 0 ? (
          <TouchableOpacity style={fcStyles.addBtn} onPress={onAdd}>
            <Text style={fcStyles.addBtnText}>+ Buyurtma</Text>
          </TouchableOpacity>
        ) : (
          <View style={fcStyles.qtyRow}>
            <TouchableOpacity style={fcStyles.qtyBtn} onPress={onRemove}>
              <Text style={fcStyles.qtyBtnText}>−</Text>
            </TouchableOpacity>
            <Text style={fcStyles.qtyVal}>{qty}</Text>
            <TouchableOpacity style={fcStyles.qtyBtn} onPress={onAdd}>
              <Text style={fcStyles.qtyBtnText}>+</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
}

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe:    { flex: 1, backgroundColor: Colors.bgDark },
  centered: {
    flex: 1, backgroundColor: Colors.bgDark,
    justifyContent: 'center', alignItems: 'center', gap: 12,
  },
  loadingText: { color: Colors.textMuted, fontSize: 14 },

  header: {
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  headerTitle: { fontSize: 18, fontWeight: '800', color: Colors.textMain },
  headerSub:   { fontSize: 12, color: Colors.textMuted, marginTop: 2 },

  catRow: { paddingHorizontal: 12, paddingVertical: 10, gap: 8 },
  catChip: {
    paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20,
    backgroundColor: Colors.bgCard, borderWidth: 1, borderColor: Colors.borderLight,
  },
  catChipActive: {
    backgroundColor: Colors.indigoAlpha15, borderColor: 'rgba(99,102,241,0.4)',
  },
  catChipText: { fontSize: 12, color: Colors.textMuted, fontWeight: '600' },
  catChipTextActive: { color: Colors.primaryLight },

  grid:    { paddingHorizontal: 10, paddingTop: 4 },
  gridRow: { gap: 10, marginBottom: 10 },

  emptyWrap: { alignItems: 'center', paddingTop: 60, gap: 10 },
  emptyEmoji: { fontSize: 48 },
  emptyText:  { color: Colors.textMuted, fontSize: 15 },

  // Float savat tugmasi
  cartFloatWrap: {
    position: 'absolute', bottom: 16, left: 16, right: 16,
  },
  cartFloatBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: Colors.primary, borderRadius: 14,
    paddingHorizontal: 18, paddingVertical: 14,
    shadowColor: Colors.primary, shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.5, shadowRadius: 12, elevation: 10,
  },
  cartFloatEmoji: { fontSize: 22 },
  cartFloatLabel: { flex: 1, color: Colors.textMain, fontWeight: '700', fontSize: 14 },
  cartFloatTotal: { color: Colors.textMain, fontWeight: '800', fontSize: 15 },

  // Modal
  modalOverlay: {
    flex: 1, justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.6)',
  },
  modalCard: {
    backgroundColor: Colors.bgCard,
    borderTopLeftRadius: 24, borderTopRightRadius: 24,
    maxHeight: '90%', paddingHorizontal: 16, paddingTop: 16,
  },
  modalHeader: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginBottom: 16,
  },
  modalTitle:    { fontSize: 17, fontWeight: '800', color: Colors.textMain },
  modalCloseBtn: { fontSize: 20, color: Colors.textMuted, padding: 4 },

  cartItem: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingVertical: 10,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  cartItemName:  { fontSize: 13, fontWeight: '600', color: Colors.textMain },
  cartItemPrice: { fontSize: 11, color: Colors.textMuted, marginTop: 2 },
  cartItemTotal: { fontSize: 13, fontWeight: '700', color: Colors.primaryLight },

  qtyRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  qtyBtn: {
    width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center',
    backgroundColor: Colors.bgSurface, borderWidth: 1, borderColor: Colors.borderSubtle,
  },
  qtyBtnText: { color: Colors.textMain, fontSize: 16, fontWeight: '700' },
  qtyVal:     { color: Colors.textMain, fontSize: 14, fontWeight: '800', minWidth: 20, textAlign: 'center' },

  totalRow: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: 14, marginBottom: 4,
  },
  totalLabel: { fontSize: 15, fontWeight: '700', color: Colors.textMuted },
  totalValue: { fontSize: 18, fontWeight: '900', color: Colors.primaryLight },

  formLabel: {
    fontSize: 12, fontWeight: '700', color: Colors.textMuted,
    marginTop: 12, marginBottom: 6,
  },
  input: {
    backgroundColor: Colors.bgSurface, borderWidth: 1, borderColor: Colors.borderSubtle,
    borderRadius: 10, paddingHorizontal: 14, paddingVertical: 11,
    color: Colors.textMain, fontSize: 14,
  },

  orderTypeRow: { flexDirection: 'row', gap: 8, marginBottom: 4 },
  orderTypeBtn: {
    flex: 1, paddingVertical: 9, borderRadius: 9,
    backgroundColor: Colors.bgSurface, borderWidth: 1, borderColor: Colors.borderLight,
    alignItems: 'center',
  },
  orderTypeBtnActive: {
    backgroundColor: Colors.indigoAlpha15, borderColor: 'rgba(99,102,241,0.4)',
  },
  orderTypeBtnText:       { fontSize: 11, fontWeight: '600', color: Colors.textMuted },
  orderTypeBtnTextActive: { color: Colors.primaryLight, fontWeight: '700' },

  submitBtn: {
    backgroundColor: Colors.primary, borderRadius: 12,
    paddingVertical: 14, alignItems: 'center', marginTop: 16,
    shadowColor: Colors.primary, shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4, shadowRadius: 8, elevation: 6,
  },
  submitBtnText: { fontSize: 15, fontWeight: '800', color: Colors.textMain },
});

const fcStyles = StyleSheet.create({
  card: {
    flex: 1, backgroundColor: Colors.bgCard, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderLight, overflow: 'hidden',
  },
  image: { width: '100%', height: 120, backgroundColor: Colors.bgSurface },
  body:  { padding: 10, gap: 4 },
  name:  { fontSize: 13, fontWeight: '700', color: Colors.textMain, lineHeight: 18 },
  category: { fontSize: 10, color: Colors.primaryLight, fontWeight: '600' },
  prepTime: { fontSize: 10, color: Colors.textDim },
  price: { fontSize: 14, fontWeight: '800', color: Colors.amberLight, marginTop: 2 },
  addBtn: {
    backgroundColor: Colors.indigoAlpha15, borderWidth: 1,
    borderColor: 'rgba(99,102,241,0.35)',
    borderRadius: 8, paddingVertical: 7, alignItems: 'center', marginTop: 4,
  },
  addBtnText: { fontSize: 12, fontWeight: '700', color: Colors.primaryLight },
  qtyRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginTop: 6,
  },
  qtyBtn: {
    width: 30, height: 30, borderRadius: 8, alignItems: 'center', justifyContent: 'center',
    backgroundColor: Colors.bgSurface, borderWidth: 1, borderColor: Colors.borderSubtle,
  },
  qtyBtnText: { fontSize: 18, fontWeight: '700', color: Colors.textMain },
  qtyVal:     { fontSize: 15, fontWeight: '800', color: Colors.textMain },
});
