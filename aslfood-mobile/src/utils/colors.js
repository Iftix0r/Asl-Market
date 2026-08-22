/**
 * AslFood — Rang palitrasini markazlashtirish
 * Web versiyaning dark glassmorphism dizayniga mos
 */

export const Colors = {
  // Asosiy fon
  bgDark: '#0b0f19',
  bgCard: '#151c2c',
  bgSurface: '#1e293b',
  bgModal: '#0f1624',

  // Accent ranglar
  primary: '#4f46e5',
  primaryLight: '#6366f1',
  emerald: '#10b981',
  emeraldDark: '#059669',
  amber: '#f59e0b',
  amberLight: '#fbbf24',
  rose: '#f43f5e',
  sky: '#38bdf8',

  // Matn
  textMain: '#f8fafc',
  textMuted: '#94a3b8',
  textDim: '#64748b',

  // Chegara
  borderLight: 'rgba(255,255,255,0.07)',
  borderSubtle: 'rgba(255,255,255,0.12)',

  // Status ranglari
  statusNew: '#f59e0b',
  statusPreparing: '#818cf8',
  statusDelivering: '#38bdf8',
  statusCompleted: '#10b981',
  statusCancelled: '#f43f5e',

  // Foydali shaffofliklar
  amberAlpha15: 'rgba(245,158,11,0.15)',
  amberAlpha30: 'rgba(245,158,11,0.30)',
  indigoAlpha15: 'rgba(99,102,241,0.15)',
  emeraldAlpha15: 'rgba(16,185,129,0.15)',
  roseAlpha15: 'rgba(244,63,94,0.15)',
  skyAlpha15: 'rgba(56,189,248,0.15)',
};

/** Status bo'yicha rang */
export function statusColor(status) {
  switch (status) {
    case 'new': return Colors.statusNew;
    case 'preparing': return Colors.statusPreparing;
    case 'delivering': return Colors.statusDelivering;
    case 'completed': return Colors.statusCompleted;
    case 'cancelled': return Colors.statusCancelled;
    default: return Colors.textMuted;
  }
}

/** Status bo'yicha emoji */
export function statusEmoji(status) {
  switch (status) {
    case 'new': return '🟡';
    case 'preparing': return '🍳';
    case 'delivering': return '🛵';
    case 'completed': return '✅';
    case 'cancelled': return '🔴';
    default: return '❓';
  }
}
