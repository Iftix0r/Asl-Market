/**
 * OrderTrackingScreen — Buyurtma holati kuzatish
 *
 * Mijoz buyurtma kodini kiritib, real-vaqtda holatini ko'radi.
 * 4 bosqichli progress bar: Yangi → Tayyorlanmoqda → Kuryerda → Yakunlandi
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  SafeAreaView, StatusBar, ScrollView, ActivityIndicator,
  Alert,
} from 'react-native';

import { trackOrder } from '../services/api';
import { Colors, statusColor, statusEmoji } from '../utils/colors';
import { formatPrice, formatDate, orderTypeLabel } from '../utils/format';

const STEPS = [
  { key: 'new',        step: 1, emoji: '📋', label: 'Qabul qilindi' },
  { key: 'preparing',  step: 2, emoji: '🍳', label: 'Tayyorlanmoqda' },
  { key: 'delivering', step: 3, emoji: '🛵', label: 'Yo\'lda' },
  { key: 'completed',  step: 4, emoji: '✅', label: 'Topshirildi' },
];

export default function OrderTrackingScreen({ route }) {
  // CustomerMenuScreen dan o'tilganda order_code parametri kelishi mumkin
  const initialCode = route?.params?.orderCode || '';

  const [code,      setCode]      = useState(initialCode);
  const [order,     setOrder]     = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [searched,  setSearched]  = useState(false);

  // Agar code kelgan bo'lsa avtomatik qidirish
  useEffect(() => {
    if (initialCode) handleSearch(initialCode);
  }, []); // eslint-disable-line

  const handleSearch = async (searchCode) => {
    const val = (searchCode || code).trim().toUpperCase();
    if (!val) { Alert.alert('Xatolik', 'Buyurtma kodini kiriting'); return; }

    setLoading(true);
    setSearched(true);
    const res = await trackOrder(val);
    setLoading(false);

    if (res.success) {
      setOrder(res.order);
    } else {
      setOrder(null);
      Alert.alert('Topilmadi', `"${val}" kodi bo'yicha buyurtma topilmadi`);
    }
  };

  const currentStep = order?.status_step || 0;

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📍 Buyurtma Kuzatish</Text>
        <Text style={styles.headerSub}>Buyurtma kodingizni kiriting</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">

        {/* Qidiruv qutisi */}
        <View style={styles.searchBox}>
          <TextInput
            style={styles.searchInput}
            placeholder="Masalan: FOOD-AB12CD"
            placeholderTextColor={Colors.textDim}
            value={code}
            onChangeText={setCode}
            autoCapitalize="characters"
            autoCorrect={false}
          />
          <TouchableOpacity
            style={[styles.searchBtn, loading && { opacity: 0.6 }]}
            onPress={() => handleSearch()}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color={Colors.bgDark} />
            ) : (
              <Text style={styles.searchBtnText}>Qidirish</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Buyurtma topilmagan */}
        {searched && !loading && !order && (
          <View style={styles.notFoundWrap}>
            <Text style={styles.notFoundEmoji}>🔍</Text>
            <Text style={styles.notFoundText}>Buyurtma topilmadi</Text>
            <Text style={styles.notFoundSub}>
              Kodni tekshirib qayta urinib ko'ring
            </Text>
          </View>
        )}

        {/* Buyurtma topildi */}
        {order && (
          <>
            {/* Status sarlavha */}
            <View style={[
              styles.statusBanner,
              { backgroundColor: statusColor(order.status) + '20',
                borderColor: statusColor(order.status) + '50' },
            ]}>
              <Text style={styles.statusBannerEmoji}>
                {statusEmoji(order.status)}
              </Text>
              <View>
                <Text style={[styles.statusBannerText, { color: statusColor(order.status) }]}>
                  {order.status_display}
                </Text>
                <Text style={styles.statusBannerCode}>#{order.order_code}</Text>
              </View>
            </View>

            {/* Progress bar */}
            {order.status !== 'cancelled' && (
              <View style={styles.progressWrap}>
                {STEPS.map((step, idx) => {
                  const done    = step.step <= currentStep;
                  const active  = step.step === currentStep;
                  const isLast  = idx === STEPS.length - 1;

                  return (
                    <React.Fragment key={step.key}>
                      <View style={styles.stepWrap}>
                        <View style={[
                          styles.stepCircle,
                          done   && styles.stepCircleDone,
                          active && styles.stepCircleActive,
                        ]}>
                          <Text style={styles.stepEmoji}>{step.emoji}</Text>
                        </View>
                        <Text style={[
                          styles.stepLabel,
                          done && styles.stepLabelDone,
                        ]}>
                          {step.label}
                        </Text>
                      </View>
                      {!isLast && (
                        <View style={[
                          styles.stepLine,
                          done && idx < currentStep - 1 && styles.stepLineDone,
                        ]} />
                      )}
                    </React.Fragment>
                  );
                })}
              </View>
            )}

            {order.status === 'cancelled' && (
              <View style={styles.cancelledBadge}>
                <Text style={styles.cancelledText}>
                  🔴 Buyurtma bekor qilindi
                </Text>
              </View>
            )}

            {/* Buyurtma tafsilotlari */}
            <View style={styles.detailCard}>
              <DetailRow label="Mijoz"       value={order.customer_name} />
              <DetailRow label="Buyurtma turi" value={orderTypeLabel(order.order_type)} />
              <DetailRow label="Vaqt"         value={formatDate(order.created_at)} />
              {order.delivery_address ? (
                <DetailRow label="Manzil" value={order.delivery_address} />
              ) : null}
            </View>

            {/* Buyurtma tarkibi */}
            <Text style={styles.sectionTitle}>Buyurtma tarkibi</Text>
            <View style={styles.itemsCard}>
              {order.items.map((item, i) => (
                <View key={i} style={styles.itemRow}>
                  <Text style={styles.itemName}>
                    {item.quantity}× {item.food_name}
                  </Text>
                  <Text style={styles.itemTotal}>{formatPrice(item.total_price)}</Text>
                </View>
              ))}
              <View style={styles.itemRowTotal}>
                <Text style={styles.itemRowTotalLabel}>Jami summa:</Text>
                <Text style={styles.itemRowTotalValue}>{formatPrice(order.total_amount)}</Text>
              </View>
            </View>

            {/* Qayta qidirish */}
            <TouchableOpacity
              style={styles.resetBtn}
              onPress={() => { setOrder(null); setSearched(false); setCode(''); }}
            >
              <Text style={styles.resetBtnText}>🔄 Boshqa buyurtma kuzatish</Text>
            </TouchableOpacity>
          </>
        )}

        {/* Boshlang'ich holat */}
        {!searched && !order && (
          <View style={styles.placeholderWrap}>
            <Text style={styles.placeholderEmoji}>📦</Text>
            <Text style={styles.placeholderTitle}>Buyurtmangizni kuzating</Text>
            <Text style={styles.placeholderSub}>
              Buyurtma bergandan keyin SMS yoki ekranda ko'rsatilgan kodni kiriting
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Yordamchi komponentlar ───────────────────────────────────────────────────

function DetailRow({ label, value }) {
  return (
    <View style={drStyles.row}>
      <Text style={drStyles.label}>{label}</Text>
      <Text style={drStyles.value}>{value}</Text>
    </View>
  );
}

const drStyles = StyleSheet.create({
  row: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', paddingVertical: 8,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  label: { fontSize: 12, color: Colors.textMuted, fontWeight: '600' },
  value: { fontSize: 13, color: Colors.textMain, fontWeight: '600', flex: 1, textAlign: 'right' },
});

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe:   { flex: 1, backgroundColor: Colors.bgDark },
  header: {
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  headerTitle: { fontSize: 18, fontWeight: '800', color: Colors.textMain },
  headerSub:   { fontSize: 12, color: Colors.textMuted, marginTop: 2 },

  scroll: { padding: 16, gap: 16, paddingBottom: 40 },

  // Qidiruv
  searchBox: { flexDirection: 'row', gap: 10 },
  searchInput: {
    flex: 1, backgroundColor: Colors.bgCard, borderWidth: 1,
    borderColor: Colors.borderSubtle, borderRadius: 10,
    paddingHorizontal: 14, paddingVertical: 12,
    color: Colors.textMain, fontSize: 14, fontWeight: '700',
  },
  searchBtn: {
    backgroundColor: Colors.primary, borderRadius: 10,
    paddingHorizontal: 16, justifyContent: 'center', alignItems: 'center',
  },
  searchBtnText: { color: Colors.textMain, fontWeight: '800', fontSize: 13 },

  // Topilmadi
  notFoundWrap:  { alignItems: 'center', paddingTop: 40, gap: 8 },
  notFoundEmoji: { fontSize: 48 },
  notFoundText:  { fontSize: 17, fontWeight: '700', color: Colors.textMain },
  notFoundSub:   { fontSize: 13, color: Colors.textMuted, textAlign: 'center' },

  // Status banner
  statusBanner: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    borderRadius: 14, borderWidth: 1, padding: 16,
  },
  statusBannerEmoji: { fontSize: 36 },
  statusBannerText:  { fontSize: 17, fontWeight: '800' },
  statusBannerCode:  { fontSize: 12, color: Colors.textMuted, marginTop: 2 },

  // Progress
  progressWrap: {
    flexDirection: 'row', alignItems: 'flex-start',
    justifyContent: 'center', paddingVertical: 8,
  },
  stepWrap: { alignItems: 'center', width: 66 },
  stepCircle: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: Colors.bgSurface, borderWidth: 2,
    borderColor: Colors.borderSubtle, alignItems: 'center', justifyContent: 'center',
  },
  stepCircleDone:   { borderColor: Colors.emerald, backgroundColor: Colors.emeraldAlpha15 },
  stepCircleActive: { borderColor: Colors.amberLight, backgroundColor: Colors.amberAlpha15 },
  stepEmoji:  { fontSize: 18 },
  stepLabel:  { fontSize: 10, color: Colors.textDim, textAlign: 'center', marginTop: 4 },
  stepLabelDone: { color: Colors.emerald, fontWeight: '700' },
  stepLine: {
    flex: 1, height: 2, backgroundColor: Colors.borderLight,
    marginTop: 21, maxWidth: 24,
  },
  stepLineDone: { backgroundColor: Colors.emerald },

  // Bekor
  cancelledBadge: {
    backgroundColor: Colors.roseAlpha15, borderRadius: 10,
    borderWidth: 1, borderColor: Colors.rose + '50',
    padding: 12, alignItems: 'center',
  },
  cancelledText: { color: Colors.rose, fontWeight: '700', fontSize: 14 },

  // Tafsilotlar
  detailCard: {
    backgroundColor: Colors.bgCard, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderLight, padding: 14,
  },
  sectionTitle: {
    fontSize: 13, fontWeight: '700', color: Colors.textMuted,
    textTransform: 'uppercase', letterSpacing: 0.5,
  },
  itemsCard: {
    backgroundColor: Colors.bgCard, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderLight, overflow: 'hidden',
  },
  itemRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingHorizontal: 14, paddingVertical: 10,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  itemName:  { fontSize: 13, color: Colors.textMain, flex: 1 },
  itemTotal: { fontSize: 13, fontWeight: '700', color: Colors.amberLight },
  itemRowTotal: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingHorizontal: 14, paddingVertical: 12,
  },
  itemRowTotalLabel: { fontSize: 14, fontWeight: '700', color: Colors.textMuted },
  itemRowTotalValue: { fontSize: 16, fontWeight: '900', color: Colors.primaryLight },

  resetBtn: {
    borderWidth: 1, borderColor: Colors.borderSubtle, borderRadius: 10,
    paddingVertical: 12, alignItems: 'center', backgroundColor: Colors.bgCard,
  },
  resetBtnText: { color: Colors.textMuted, fontSize: 13, fontWeight: '600' },

  // Placeholder
  placeholderWrap:  { alignItems: 'center', paddingTop: 60, gap: 12 },
  placeholderEmoji: { fontSize: 60 },
  placeholderTitle: { fontSize: 18, fontWeight: '800', color: Colors.textMain },
  placeholderSub:   {
    fontSize: 13, color: Colors.textMuted, textAlign: 'center', lineHeight: 20,
  },
});
