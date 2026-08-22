/**
 * HomeScreen — Mode tanlash ekrani
 * Oshpaz paneli yoki Mijoz panelini tanlash
 */

import React from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  StatusBar, SafeAreaView,
} from 'react-native';
import { Colors } from '../utils/colors';

export default function HomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />

      {/* Logo & Sarlavha */}
      <View style={styles.header}>
        <Text style={styles.logo}>🍔</Text>
        <Text style={styles.brandName}>AslFood</Text>
        <Text style={styles.brandSub}>Fast-Food Boshqaruv Tizimi</Text>
      </View>

      {/* Mode tugmalari */}
      <View style={styles.cards}>

        {/* Oshpaz paneli */}
        <TouchableOpacity
          style={[styles.card, styles.cardKitchen]}
          onPress={() => navigation.navigate('KitchenPanel')}
          activeOpacity={0.85}
        >
          <Text style={styles.cardEmoji}>👨‍🍳</Text>
          <Text style={styles.cardTitle}>Oshpaz Paneli</Text>
          <Text style={styles.cardDesc}>
            Buyurtmalar board, menyu boshqaruvi va daromad statistikasi
          </Text>
          <View style={[styles.cardBadge, { backgroundColor: Colors.amberAlpha30 }]}>
            <Text style={[styles.cardBadgeText, { color: Colors.amberLight }]}>
              Kitchen & Admin
            </Text>
          </View>
        </TouchableOpacity>

        {/* Mijoz paneli */}
        <TouchableOpacity
          style={[styles.card, styles.cardCustomer]}
          onPress={() => navigation.navigate('CustomerPanel')}
          activeOpacity={0.85}
        >
          <Text style={styles.cardEmoji}>🛍️</Text>
          <Text style={styles.cardTitle}>Mijoz Ilovasi</Text>
          <Text style={styles.cardDesc}>
            Taomlarni ko'rish, buyurtma berish va holat kuzatish
          </Text>
          <View style={[styles.cardBadge, { backgroundColor: Colors.indigoAlpha15 }]}>
            <Text style={[styles.cardBadgeText, { color: Colors.primaryLight }]}>
              Buyurtma berish
            </Text>
          </View>
        </TouchableOpacity>
      </View>

      <Text style={styles.footer}>AslMarket.uz © 2026</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bgDark,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  logo: {
    fontSize: 64,
    marginBottom: 12,
  },
  brandName: {
    fontSize: 36,
    fontWeight: '800',
    color: Colors.textMain,
    letterSpacing: -1,
  },
  brandSub: {
    fontSize: 14,
    color: Colors.textMuted,
    marginTop: 4,
  },
  cards: {
    width: '100%',
    gap: 16,
  },
  card: {
    borderRadius: 18,
    padding: 24,
    borderWidth: 1,
    gap: 8,
  },
  cardKitchen: {
    backgroundColor: 'rgba(245,158,11,0.08)',
    borderColor: Colors.amberAlpha30,
  },
  cardCustomer: {
    backgroundColor: Colors.indigoAlpha15,
    borderColor: 'rgba(99,102,241,0.3)',
  },
  cardEmoji: {
    fontSize: 36,
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: Colors.textMain,
    letterSpacing: -0.5,
  },
  cardDesc: {
    fontSize: 13,
    color: Colors.textMuted,
    lineHeight: 19,
  },
  cardBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 999,
    marginTop: 4,
  },
  cardBadgeText: {
    fontSize: 12,
    fontWeight: '700',
  },
  footer: {
    position: 'absolute',
    bottom: 28,
    fontSize: 12,
    color: Colors.textDim,
  },
});
