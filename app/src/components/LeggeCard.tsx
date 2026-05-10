// ============================================================
// EdilEngine - LeggeCard Component
// ============================================================

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';
import type { LeggeBase } from '../services/types';

interface LeggeCardProps {
  legge: LeggeBase;
  onPress?: (legge: LeggeBase) => void;
  onChatPress?: (legge: LeggeBase) => void;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'N/D';
  try {
    return new Date(dateStr).toLocaleDateString('it-IT', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getTipoBadgeStyle(tipo: string | null): { bg: string; text: string } {
  if (!tipo) return { bg: colors.slate[100], text: colors.slate[700] };
  const t = tipo.toLowerCase();
  if (t.includes('legge') || t.includes('l.')) return { bg: colors.primary[100], text: colors.primary[700] };
  if (t.includes('decreto') || t.includes('d.l.') || t.includes('d.p.r.')) return { bg: '#dbeafe', text: '#1e40af' };
  if (t.includes('regolamento') || t.includes('direttiva')) return { bg: '#fef3c7', text: '#92400e' };
  if (t.includes('circolare') || t.includes('linee guida')) return { bg: colors.green[100], text: colors.green[700] };
  return { bg: colors.slate[100], text: colors.slate[700] };
}

export default function LeggeCard({ legge, onPress, onChatPress }: LeggeCardProps) {
  const badgeStyle = getTipoBadgeStyle(legge.tipo);

  const handlePress = () => {
    if (onPress) onPress(legge);
  };

  const handleChatPress = (e: any) => {
    e.stopPropagation?.();
    if (onChatPress) onChatPress(legge);
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={handlePress}
      activeOpacity={0.7}
      accessibilityLabel={`Legge: ${legge.titolo}`}
    >
      <View style={styles.content}>
        {/* Tipo badge */}
        {legge.tipo && (
          <View style={[styles.badge, { backgroundColor: badgeStyle.bg }]}>
            <Text style={[styles.badgeText, { color: badgeStyle.text }]}>
              {legge.tipo}
            </Text>
          </View>
        )}

        {/* Titolo */}
        <Text style={styles.title} numberOfLines={2}>
          {legge.titolo}
        </Text>

        {/* Meta info */}
        <View style={styles.meta}>
          {legge.numero && (
            <View style={styles.metaItem}>
              <Ionicons name="document-text-outline" size={14} color={colors.slate[500]} />
              <Text style={styles.metaText}>n. {legge.numero}</Text>
            </View>
          )}
          {legge.data_emanazione && (
            <View style={styles.metaItem}>
              <Ionicons name="calendar-outline" size={14} color={colors.slate[500]} />
              <Text style={styles.metaText}>{formatDate(legge.data_emanazione)}</Text>
            </View>
          )}
          {legge.autorita && (
            <View style={styles.metaItem}>
              <Ionicons name="business-outline" size={14} color={colors.slate[500]} />
              <Text style={styles.metaText} numberOfLines={1}>
                {legge.autorita.length > 40 ? legge.autorita.slice(0, 40) + '…' : legge.autorita}
              </Text>
            </View>
          )}
        </View>

        {/* Chat button overlay at bottom */}
        {onChatPress && (
          <TouchableOpacity
            style={styles.chatButton}
            onPress={handleChatPress}
            accessibilityLabel="Chiedi al chatbot"
          >
            <Ionicons name="chatbubble-ellipses-outline" size={14} color={colors.primary[600]} />
            <Text style={styles.chatButtonText}>Chiedi al chatbot</Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.slate[200],
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
    marginBottom: 12,
  },
  content: {
    padding: 16,
  },
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    marginBottom: 10,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.slate[900],
    lineHeight: 22,
    marginBottom: 10,
  },
  meta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 4,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: 12,
    color: colors.slate[500],
    maxWidth: 130,
  },
  chatButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.slate[100],
  },
  chatButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: colors.primary[600],
  },
});
