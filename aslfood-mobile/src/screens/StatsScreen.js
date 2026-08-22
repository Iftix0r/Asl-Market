/**
 * StatsScreen — Daromad statistikasi va tahlil
 *
 * - Bugungi / Haftalik / Umumiy daromad
 * - Faol buyurtmalar soni (real-vaqt)
 * - Top-5 ko'p sotilgan taomlar
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, ScrollView, StyleSheet,
  SafeAreaView, StatusBar, RefreshControl,
  ActivityIndicator, TouchableOpacity,
} from 'react-native';

import { getStats } from '../services/api';
import { Colors } from '../utils/colors';
import { formatPrice } from '../utils/format';

export default function StatsScreen() {
  const [stats,      setStats]      = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = useCallback(async () => {
    const res = await getStats();
    if (res.success) setStats(res.stats);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.amberLight} />
        <Text style={styles.loadingText}>Statistika yuklanmoqda...</Text>
      </View>
    );
  }

  if (!stats) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorEmoji}>⚠️</Text>
        <Text style={styles.errorText}>Ma'lumot yuklanmadi</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={fetchStats}>
          <Text style={styles.retryBtnText}>Qayta urinish</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { today, week, total, active_now, top_items } = stats;

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📊 Statistika</Text>
        <TouchableOpacity
          style={styles.refreshBtn}
          onPress={() => { setRefreshing(true); fetchStats(); }}
        >
          <Text style={styles.refreshBtnText}>🔄</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => { setRefreshing(true); fetchStats(); }}
            tintColor={Colors.amberLight}
          />
        }
      >

        {/* Faol holatlar */}
        <SectionTitle title="🔴 Hozirgi Faol Buyurtmalar" />
        <View style={styles.activeRow}>
          <ActiveBadge emoji="🟡" label="Yangi"          count={active_now.new}        color={Colors.statusNew} />
          <ActiveBadge emoji="🍳" label="Tayyorlanmoqda" count={active_now.preparing}  color={Colors.statusPreparing} />
          <ActiveBadge emoji="🛵" label="Kuryerda"        count={active_now.delivering} color={Colors.statusDelivering} />
        </View>

        {/* Bugun */}
        <SectionTitle title="📅 Bugun" />
        <View style={styles.metricsRow}>
          <MetricCard
            label="Tushum"
            value={formatPrice(today.revenue)}
            color={Colors.emerald}
            emoji="💰"
          />
          <MetricCard
            label="Buyurtmalar"
            value={String(today.orders_count)}
            color={Colors.sky}
            emoji="📋"
          />
          <MetricCard
            label="Yakunlandi"
            value={String(today.completed_count)}
            color={Colors.amberLight}
            emoji="✅"
          />
        </View>

        {/* Hafta */}
        <SectionTitle title="📆 So'nggi 7 kun" />
        <View style={styles.metricsRow}>
          <MetricCard
            label="Tushum"
            value={formatPrice(week.revenue)}
            color={Colors.emerald}
            emoji="💰"
          />
          <MetricCard
            label="Buyurtmalar"
            value={String(week.orders_count)}
            color={Colors.sky}
            emoji="📋"
          />
          <MetricCard
            label="Yakunlandi"
            value={String(week.completed_count)}
            color={Colors.amberLight}
            emoji="✅"
          />
        </View>

        {/* Umumiy */}
        <SectionTitle title="🏆 Barcha vaqt" />
        <View style={styles.bigMetricsRow}>
          <BigMetricCard
            label="Jami Tushum"
            value={formatPrice(total.revenue)}
            color={Colors.primary}
            emoji="💎"
          />
          <BigMetricCard
            label="Jami Yakunlangan"
            value={`${total.completed_orders} ta`}
            color={Colors.emerald}
            emoji="🏅"
          />
        </View>

        {/* Top taomlar */}
        {top_items && top_items.length > 0 && (
          <>
            <SectionTitle title="🌟 Eng Ko'p Sotilgan Taomlar" />
            <View style={styles.topItemsCard}>
              {top_items.map((item, index) => (
                <View key={index} style={styles.topItemRow}>
                  <View style={styles.topItemRank}>
                    <Text style={styles.topItemRankText}>
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                    </Text>
                  </View>
                  <Text style={styles.topItemName} numberOfLines={1}>
                    {item.food_name}
                  </Text>
                  <View style={styles.topItemQtyWrap}>
                    <Text style={styles.topItemQty}>{item.total_qty} ta</Text>
                  </View>
                </View>
              ))}
            </View>
          </>
        )}

        {/* Pastki bo'shliq */}
        <View style={{ height: 24 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Yordamchi komponentlar ───────────────────────────────────────────────────

function SectionTitle({ title }) {
  return <Text style={styles.sectionTitle}>{title}</Text>;
}

function ActiveBadge({ emoji, label, count, color }) {
  return (
    <View style={[styles.activeBadge, { borderColor: color + '50', backgroundColor: color + '15' }]}>
      <Text style={styles.activeBadgeEmoji}>{emoji}</Text>
      <Text style={[styles.activeBadgeCount, { color }]}>{count}</Text>
      <Text style={styles.activeBadgeLabel}>{label}</Text>
    </View>
  );
}

function MetricCard({ label, value, color, emoji }) {
  return (
    <View style={styles.metricCard}>
      <Text style={styles.metricEmoji}>{emoji}</Text>
      <Text style={[styles.metricValue, { color }]}>{value}</Text>
      <Text style={styles.metricLabel}>{label}</Text>
    </View>
  );
}

function BigMetricCard({ label, value, color, emoji }) {
  return (
    <View style={[styles.bigMetricCard, { borderColor: color + '40' }]}>
      <Text style={styles.bigMetricEmoji}>{emoji}</Text>
      <Text style={[styles.bigMetricValue, { color }]}>{value}</Text>
      <Text style={styles.bigMetricLabel}>{label}</Text>
    </View>
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
  errorEmoji: { fontSize: 48 },
  errorText: { color: Colors.textMuted, fontSize: 16 },
  retryBtn: {
    marginTop: 8, backgroundColor: Colors.bgCard, borderRadius: 10,
    paddingHorizontal: 20, paddingVertical: 10, borderWidth: 1, borderColor: Colors.borderSubtle,
  },
  retryBtnText: { color: Colors.primaryLight, fontWeight: '700' },

  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  headerTitle: { fontSize: 18, fontWeight: '800', color: Colors.textMain },
  refreshBtn: { padding: 8, borderRadius: 10, backgroundColor: Colors.bgCard },
  refreshBtnText: { fontSize: 18 },

  scroll: { padding: 16, gap: 12 },

  sectionTitle: {
    fontSize: 13, fontWeight: '700', color: Colors.textMuted,
    textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 8,
  },

  activeRow: { flexDirection: 'row', gap: 10 },
  activeBadge: {
    flex: 1, alignItems: 'center', paddingVertical: 12,
    borderRadius: 12, borderWidth: 1, gap: 3,
  },
  activeBadgeEmoji: { fontSize: 20 },
  activeBadgeCount: { fontSize: 24, fontWeight: '900' },
  activeBadgeLabel: { fontSize: 10, color: Colors.textMuted, textAlign: 'center' },

  metricsRow: { flexDirection: 'row', gap: 10 },
  metricCard: {
    flex: 1, backgroundColor: Colors.bgCard, borderRadius: 12,
    padding: 14, alignItems: 'center', borderWidth: 1, borderColor: Colors.borderLight, gap: 4,
  },
  metricEmoji: { fontSize: 20 },
  metricValue: { fontSize: 16, fontWeight: '800' },
  metricLabel: { fontSize: 10, color: Colors.textMuted },

  bigMetricsRow: { flexDirection: 'row', gap: 10 },
  bigMetricCard: {
    flex: 1, backgroundColor: Colors.bgCard, borderRadius: 14,
    padding: 18, alignItems: 'center', borderWidth: 1, gap: 6,
  },
  bigMetricEmoji: { fontSize: 28 },
  bigMetricValue: { fontSize: 18, fontWeight: '900' },
  bigMetricLabel: { fontSize: 12, color: Colors.textMuted, textAlign: 'center' },

  topItemsCard: {
    backgroundColor: Colors.bgCard, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderLight, overflow: 'hidden',
  },
  topItemRow: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
    gap: 10,
  },
  topItemRank: { width: 28, alignItems: 'center' },
  topItemRankText: { fontSize: 18 },
  topItemName: { flex: 1, fontSize: 13, fontWeight: '600', color: Colors.textMain },
  topItemQtyWrap: {
    backgroundColor: Colors.amberAlpha15, borderRadius: 8,
    paddingHorizontal: 10, paddingVertical: 4,
  },
  topItemQty: { fontSize: 12, fontWeight: '700', color: Colors.amberLight },
});
