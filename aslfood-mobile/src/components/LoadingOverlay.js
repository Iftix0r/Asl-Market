/**
 * LoadingOverlay — To'liq ekran yuklash ko'rsatkichi
 */

import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { Colors } from '../utils/colors';

export default function LoadingOverlay({ message = 'Yuklanmoqda...' }) {
  return (
    <View style={styles.overlay}>
      <ActivityIndicator size="large" color={Colors.amberLight} />
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1, backgroundColor: Colors.bgDark,
    justifyContent: 'center', alignItems: 'center', gap: 14,
  },
  text: { color: Colors.textMuted, fontSize: 14 },
});
