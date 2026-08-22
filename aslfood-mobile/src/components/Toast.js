/**
 * Toast — Qisqa bildirishnoma komponenti
 *
 * Ishlatish:
 *   import Toast, { showToast } from '../components/Toast';
 *
 *   // Komponentda:
 *   <Toast />
 *
 *   // Istalgan yerda chaqirish:
 *   showToast('Muvaffaqiyat!', 'success');
 *   showToast('Xatolik yuz berdi', 'error');
 *   showToast('Ogohlantirish', 'warning');
 */

import React, { useState, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Colors } from '../utils/colors';

// Global callback holder
let _showToastFn = null;

export function showToast(message, type = 'success') {
  if (_showToastFn) _showToastFn(message, type);
}

export default function Toast() {
  const [visible,  setVisible]  = useState(false);
  const [message,  setMessage]  = useState('');
  const [type,     setType]     = useState('success');
  const opacity    = useRef(new Animated.Value(0)).current;
  const timerRef   = useRef(null);

  const show = useCallback((msg, t = 'success') => {
    if (timerRef.current) clearTimeout(timerRef.current);

    setMessage(msg);
    setType(t);
    setVisible(true);

    Animated.timing(opacity, {
      toValue: 1, duration: 250, useNativeDriver: true,
    }).start();

    timerRef.current = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0, duration: 300, useNativeDriver: true,
      }).start(() => setVisible(false));
    }, 2800);
  }, [opacity]);

  // Global ga ulash
  _showToastFn = show;

  if (!visible) return null;

  const bgColor = {
    success: Colors.emerald,
    error:   Colors.rose,
    warning: Colors.amber,
    info:    Colors.primaryLight,
  }[type] || Colors.primaryLight;

  const emoji = {
    success: '✅',
    error:   '❌',
    warning: '⚠️',
    info:    'ℹ️',
  }[type] || 'ℹ️';

  return (
    <Animated.View style={[styles.toast, { opacity, backgroundColor: bgColor + 'EE' }]}>
      <Text style={styles.emoji}>{emoji}</Text>
      <Text style={styles.text} numberOfLines={2}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  toast: {
    position: 'absolute',
    bottom: 90,
    left: 16,
    right: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 13,
    borderRadius: 12,
    zIndex: 9999,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 12,
  },
  emoji: { fontSize: 18 },
  text:  { flex: 1, color: '#fff', fontSize: 14, fontWeight: '600', lineHeight: 20 },
});
