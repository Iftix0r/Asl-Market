/**
 * MenuScreen — Menyu boshqaruvi (Admin/Oshpaz uchun)
 *
 * - Barcha taomlar ro'yxati
 * - Mavjud/Tugagan toggle (bir teginish)
 * - Yangi taom qo'shish (AddMenuItemScreen ga o'tadi)
 * - Taomni o'chirish (swipe yoki long-press)
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  SafeAreaView, StatusBar, Alert, ActivityIndicator,
  RefreshControl, Image,
} from 'react-native';

import { getAllMenuItems, toggleFoodItem, deleteFoodItem } from '../services/api';
import { Colors } from '../utils/colors';
import { formatPrice } from '../utils/format';

export default function MenuScreen({ navigation }) {
  const [items,      setItems]      = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [togglingId, setTogglingId] = useState(null);

  const fetchItems = useCallback(async () => {
    const res = await getAllMenuItems();
    if (res.success) setItems(res.items);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => {
    fetchItems();
    // Ekranga qaytganda ham yangilansin (AddMenuItem dan keyin)
    const unsubscribe = navigation.addListener('focus', fetchItems);
    return unsubscribe;
  }, [fetchItems, navigation]);

  // ─── Toggle ───────────────────────────────────────────────────────────────

  const handleToggle = async (item) => {
    setTogglingId(item.id);
    const res = await toggleFoodItem(item.id);
    if (res.success) {
      setItems(prev =>
        prev.map(i => i.id === item.id ? { ...i, is_available: res.is_available } : i)
      );
    } else {
      Alert.alert('Xatolik', res.error || 'Toggle amalga oshmadi');
    }
    setTogglingId(null);
  };

  // ─── O'chirish ────────────────────────────────────────────────────────────

  const handleDelete = (item) => {
    Alert.alert(
      'Taomni o\'chirish',
      `"${item.name}" ni o'chirishni tasdiqlaysizmi?`,
      [
        { text: 'Bekor', style: 'cancel' },
        {
          text: 'O\'chirish',
          style: 'destructive',
          onPress: async () => {
            const res = await deleteFoodItem(item.id);
            if (res.success) {
              setItems(prev => prev.filter(i => i.id !== item.id));
            } else {
              Alert.alert('Xatolik', res.error);
            }
          },
        },
      ]
    );
  };

  // ─── Render item ──────────────────────────────────────────────────────────

  const renderItem = ({ item }) => {
    const toggling = togglingId === item.id;

    return (
      <View style={styles.card}>
        {/* Rasm */}
        <Image
          source={{ uri: item.image_url || 'https://via.placeholder.com/80' }}
          style={styles.image}
          resizeMode="cover"
        />

        {/* Ma'lumot */}
        <View style={styles.info}>
          <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
          <Text style={styles.category}>{item.category}</Text>
          <Text style={styles.price}>{formatPrice(item.price)}</Text>
          <Text style={styles.prepTime}>⏱ ~{item.preparation_time_mins} daqiqa</Text>
        </View>

        {/* Harakatlar */}
        <View style={styles.actions}>
          {/* Toggle */}
          <TouchableOpacity
            style={[
              styles.toggleBtn,
              item.is_available ? styles.toggleAvailable : styles.toggleUnavailable,
            ]}
            onPress={() => handleToggle(item)}
            disabled={toggling}
          >
            {toggling ? (
              <ActivityIndicator size="small" color={Colors.textMain} />
            ) : (
              <Text style={styles.toggleBtnText}>
                {item.is_available ? '✅ Mavjud' : '❌ Tugagan'}
              </Text>
            )}
          </TouchableOpacity>

          {/* O'chirish */}
          <TouchableOpacity
            style={styles.deleteBtn}
            onPress={() => handleDelete(item)}
          >
            <Text style={styles.deleteBtnText}>🗑</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.amberLight} />
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
          <Text style={styles.headerTitle}>🍔 Menyu Boshqaruvi</Text>
          <Text style={styles.headerSub}>{items.length} ta taom</Text>
        </View>
        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => navigation.navigate('AddMenuItem')}
        >
          <Text style={styles.addBtnText}>+ Yangi</Text>
        </TouchableOpacity>
      </View>

      {/* Ro'yxat */}
      <FlatList
        data={items}
        keyExtractor={item => String(item.id)}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => { setRefreshing(true); fetchItems(); }}
            tintColor={Colors.amberLight}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyWrap}>
            <Text style={styles.emptyEmoji}>🍽️</Text>
            <Text style={styles.emptyText}>Hali taomlar yo'q</Text>
            <TouchableOpacity
              style={styles.emptyAddBtn}
              onPress={() => navigation.navigate('AddMenuItem')}
            >
              <Text style={styles.emptyAddBtnText}>Birinchi taomni qo'shish</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </SafeAreaView>
  );
}

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bgDark },
  centered: {
    flex: 1, backgroundColor: Colors.bgDark,
    justifyContent: 'center', alignItems: 'center', gap: 12,
  },
  loadingText: { color: Colors.textMuted, fontSize: 14 },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  headerTitle: { fontSize: 18, fontWeight: '800', color: Colors.textMain },
  headerSub: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  addBtn: {
    backgroundColor: Colors.amberAlpha15,
    borderWidth: 1,
    borderColor: Colors.amberAlpha30,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 10,
  },
  addBtnText: { color: Colors.amberLight, fontWeight: '700', fontSize: 13 },

  list: { padding: 12, gap: 10 },

  card: {
    flexDirection: 'row',
    backgroundColor: Colors.bgCard,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: Colors.borderLight,
    gap: 12,
    alignItems: 'flex-start',
  },
  image: {
    width: 72,
    height: 72,
    borderRadius: 10,
    backgroundColor: Colors.bgSurface,
  },
  info: { flex: 1, gap: 3 },
  name: { fontSize: 14, fontWeight: '700', color: Colors.textMain, lineHeight: 19 },
  category: { fontSize: 11, color: Colors.primaryLight },
  price: { fontSize: 14, fontWeight: '800', color: Colors.amberLight },
  prepTime: { fontSize: 11, color: Colors.textMuted },

  actions: { gap: 8, alignItems: 'flex-end' },
  toggleBtn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    minWidth: 90,
    alignItems: 'center',
  },
  toggleAvailable: { backgroundColor: Colors.emeraldAlpha15, borderWidth: 1, borderColor: Colors.emerald + '50' },
  toggleUnavailable: { backgroundColor: Colors.roseAlpha15, borderWidth: 1, borderColor: Colors.rose + '50' },
  toggleBtnText: { fontSize: 11, fontWeight: '700', color: Colors.textMain },

  deleteBtn: {
    padding: 6,
    borderRadius: 8,
    backgroundColor: Colors.roseAlpha15,
    borderWidth: 1,
    borderColor: Colors.rose + '40',
  },
  deleteBtnText: { fontSize: 16 },

  emptyWrap: { alignItems: 'center', paddingTop: 80, gap: 12 },
  emptyEmoji: { fontSize: 48 },
  emptyText: { color: Colors.textMuted, fontSize: 16 },
  emptyAddBtn: {
    backgroundColor: Colors.amberAlpha15,
    borderWidth: 1,
    borderColor: Colors.amberAlpha30,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
    marginTop: 8,
  },
  emptyAddBtnText: { color: Colors.amberLight, fontWeight: '700' },
});
