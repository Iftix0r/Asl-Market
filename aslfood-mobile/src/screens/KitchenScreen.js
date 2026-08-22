/**
 * KitchenScreen — Oshpaz terminali (Live Kitchen Board)
 *
 * 4 ta ustunli Kanban board:
 *   🟡 Yangi  →  🍳 Tayyorlanmoqda  →  🛵 Kuryerda  →  ✅ Yakunlandi
 *
 * Har 10 soniyada avtomatik yangilanadi.
 * Yangi buyurtma kelganda ovoz/vibra bildirishnoma.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  RefreshControl, SafeAreaView, StatusBar, Vibration,
  ActivityIndicator, Alert,
} from 'react-native';

import { getOrders, updateOrderStatus } from '../services/api';
import { Colors, statusColor } from '../utils/colors';
import { formatPrice, timeAgo, orderTypeLabel } from '../utils/format';

const COLUMNS = [
  { key: 'new',        emoji: '🟡', label: 'Yangi',          color: Colors.statusNew },
  { key: 'preparing',  emoji: '🍳', label: 'Tayyorlanmoqda', color: Colors.statusPreparing },
  { key: 'delivering', emoji: '🛵', label: 'Kuryerda',        color: Colors.statusDelivering },
  { key: 'completed',  emoji: '✅', label: 'Yakunlandi',      color: Colors.statusCompleted },
];

const NEXT_STATUS = {
  new:        { status: 'preparing',  label: '🍳 Tayyorlashni boshlash' },
  preparing:  { status: 'delivering', label: '🛵 Kuryerga berish' },
  delivering: { status: 'completed',  label: '✅ Yakunlash' },
};

export default function KitchenScreen() {
  const [orders,      setOrders]      = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [refreshing,  setRefreshing]  = useState(false);
  const [updatingId,  setUpdatingId]  = useState(null);
  const prevNewCount  = useRef(0);
  const intervalRef   = useRef(null);

  // ─── Ma'lumot yuklash ────────────────────────────────────────────────────

  const fetchOrders = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    const res = await getOrders();
    if (res.success) {
      const incoming = res.orders;
      const newCount = incoming.filter(o => o.status === 'new').length;

      // Yangi buyurtma kelganda vibra
      if (prevNewCount.current < newCount) {
        Vibration.vibrate([0, 200, 100, 200]);
      }
      prevNewCount.current = newCount;
      setOrders(incoming);
    }
    setLoading(false);
    setRefreshing(false);
  }, []);

  // Avval bir marta yuklash, keyin har 10s yangilanish
  useEffect(() => {
    fetchOrders();
    intervalRef.current = setInterval(() => fetchOrders(true), 10000);
    return () => clearInterval(intervalRef.current);
  }, [fetchOrders]);

  // ─── Holat yangilash ─────────────────────────────────────────────────────

  const handleStatusUpdate = async (orderId, currentStatus) => {
    const next = NEXT_STATUS[currentStatus];
    if (!next) return;

    Alert.alert(
      'Holatni yangilash',
      `Buyurtma #${orderId} ni "${next.label}" ga o'tkazilsinmi?`,
      [
        { text: 'Bekor', style: 'cancel' },
        {
          text: 'Ha, tasdiqlash',
          onPress: async () => {
            setUpdatingId(orderId);
            const res = await updateOrderStatus(orderId, next.status);
            if (res.success) {
              fetchOrders(true);
            } else {
              Alert.alert('Xatolik', res.error || 'Holat yangilashda xatolik');
            }
            setUpdatingId(null);
          },
        },
      ]
    );
  };

  // ─── Buyurtmalarni ustunlarga ajratish ───────────────────────────────────

  const byStatus = (status) => orders.filter(o => o.status === status);

  // ─── Render ──────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.amberLight} />
        <Text style={styles.loadingText}>Buyurtmalar yuklanmoqda...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>👨‍🍳 Oshpaz Terminali</Text>
          <Text style={styles.headerSub}>
            Faol buyurtmalar: {orders.filter(o => o.status !== 'completed').length} ta
          </Text>
        </View>
        <TouchableOpacity
          style={styles.refreshBtn}
          onPress={() => { setRefreshing(true); fetchOrders(); }}
        >
          <Text style={styles.refreshBtnText}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Ustunlar (horizontal scroll) */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.columnsContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => { setRefreshing(true); fetchOrders(); }}
            tintColor={Colors.amberLight}
          />
        }
      >
        {COLUMNS.map(col => {
          const colOrders = byStatus(col.key);
          return (
            <View key={col.key} style={styles.column}>
              {/* Ustun boshi */}
              <View style={[styles.colHeader, { borderColor: col.color + '60' }]}>
                <Text style={[styles.colHeaderText, { color: col.color }]}>
                  {col.emoji} {col.label}
                </Text>
                <View style={[styles.colBadge, { backgroundColor: col.color + '25' }]}>
                  <Text style={[styles.colBadgeText, { color: col.color }]}>
                    {colOrders.length}
                  </Text>
                </View>
              </View>

              {/* Kartalar */}
              {colOrders.length === 0 ? (
                <View style={styles.emptyCol}>
                  <Text style={styles.emptyColText}>Bo'sh</Text>
                </View>
              ) : (
                colOrders.map(order => (
                  <OrderCard
                    key={order.id}
                    order={order}
                    colColor={col.color}
                    updating={updatingId === order.id}
                    onAction={() => handleStatusUpdate(order.id, order.status)}
                    nextAction={NEXT_STATUS[order.status]}
                  />
                ))
              )}
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Buyurtma kartasi ─────────────────────────────────────────────────────────

function OrderCard({ order, colColor, updating, onAction, nextAction }) {
  return (
    <View style={[styles.card, { borderLeftColor: colColor }]}>
      {/* Kod va summa */}
      <View style={styles.cardRow}>
        <Text style={styles.cardCode}>#{order.order_code}</Text>
        <Text style={[styles.cardAmount, { color: colColor }]}>
          {formatPrice(order.total_amount)}
        </Text>
      </View>

      {/* Mijoz */}
      <Text style={styles.cardCustomer}>{order.customer_name}</Text>
      <Text style={styles.cardMeta}>
        📞 {order.phone}  •  {orderTypeLabel(order.order_type)}
      </Text>
      {order.delivery_address ? (
        <Text style={styles.cardAddress} numberOfLines={1}>
          📍 {order.delivery_address}
        </Text>
      ) : null}

      {/* Vaqt */}
      <Text style={styles.cardTime}>🕐 {timeAgo(order.created_at)}</Text>

      {/* Taomlar ro'yxati */}
      <View style={styles.itemsList}>
        {order.items.map((item, i) => (
          <Text key={i} style={styles.itemRow}>
            • {item.quantity}x {item.food_name}
          </Text>
        ))}
      </View>

      {/* Harakat tugmasi */}
      {nextAction && (
        <TouchableOpacity
          style={[styles.actionBtn, { borderColor: colColor + '60', opacity: updating ? 0.6 : 1 }]}
          onPress={onAction}
          disabled={updating}
        >
          {updating ? (
            <ActivityIndicator size="small" color={colColor} />
          ) : (
            <Text style={[styles.actionBtnText, { color: colColor }]}>
              {nextAction.label}
            </Text>
          )}
        </TouchableOpacity>
      )}
    </View>
  );
}

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.bgDark,
  },
  centered: {
    flex: 1,
    backgroundColor: Colors.bgDark,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {
    color: Colors.textMuted,
    fontSize: 14,
  },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: Colors.textMain,
  },
  headerSub: {
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 2,
  },
  refreshBtn: {
    padding: 8,
    borderRadius: 10,
    backgroundColor: Colors.bgCard,
  },
  refreshBtnText: {
    fontSize: 18,
  },

  // Ustunlar
  columnsContainer: {
    padding: 12,
    gap: 12,
    alignItems: 'flex-start',
  },
  column: {
    width: 260,
    gap: 10,
  },
  colHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    backgroundColor: Colors.bgCard,
    marginBottom: 2,
  },
  colHeaderText: {
    fontSize: 13,
    fontWeight: '700',
  },
  colBadge: {
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  colBadgeText: {
    fontSize: 12,
    fontWeight: '800',
  },
  emptyCol: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyColText: {
    color: Colors.textDim,
    fontSize: 13,
  },

  // Karta
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    padding: 14,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: Colors.borderLight,
    gap: 5,
  },
  cardRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardCode: {
    fontSize: 14,
    fontWeight: '800',
    color: Colors.textMain,
  },
  cardAmount: {
    fontSize: 13,
    fontWeight: '700',
  },
  cardCustomer: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.textMain,
  },
  cardMeta: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  cardAddress: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  cardTime: {
    fontSize: 11,
    color: Colors.textDim,
  },
  itemsList: {
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight,
    paddingTop: 6,
    marginTop: 2,
    gap: 2,
  },
  itemRow: {
    fontSize: 12,
    color: Colors.textMuted,
  },
  actionBtn: {
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: 'center',
    marginTop: 6,
    backgroundColor: Colors.bgSurface,
  },
  actionBtnText: {
    fontSize: 12,
    fontWeight: '700',
  },
});
