/**
 * StatusBadge — Buyurtma holat ko'rsatkichi
 *
 * Ishlatish:
 *   <StatusBadge status="new" />
 *   <StatusBadge status="preparing" size="lg" />
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { statusColor, statusEmoji } from '../utils/colors';

const STATUS_LABELS = {
  new:        'Yangi',
  preparing:  'Tayyorlanmoqda',
  delivering: 'Kuryerda',
  completed:  'Yakunlandi',
  cancelled:  'Bekor qilindi',
};

export default function StatusBadge({ status, size = 'sm' }) {
  const color = statusColor(status);
  const label = STATUS_LABELS[status] || status;
  const emoji = statusEmoji(status);

  const isLg = size === 'lg';

  return (
    <View style={[
      styles.badge,
      { backgroundColor: color + '20', borderColor: color + '50' },
      isLg && styles.badgeLg,
    ]}>
      <Text style={[styles.emoji, isLg && styles.emojiLg]}>{emoji}</Text>
      <Text style={[styles.label, { color }, isLg && styles.labelLg]}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: 999, borderWidth: 1,
    alignSelf: 'flex-start',
  },
  badgeLg: { paddingHorizontal: 14, paddingVertical: 7 },
  emoji:   { fontSize: 13 },
  emojiLg: { fontSize: 18 },
  label:   { fontSize: 11, fontWeight: '700' },
  labelLg: { fontSize: 14 },
});
