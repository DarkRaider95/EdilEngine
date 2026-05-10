// ============================================================
// EdilEngine - IncentivoCard Component
// ============================================================

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import type { IncentivoBase } from '../services/types';

interface IncentivoCardProps {
  incentivo: IncentivoBase;
  onPress?: (incentivo: IncentivoBase) => void;
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

function formatAliquota(value: number | null): string {
  if (value === null || value === undefined) return 'N/D';
  return `${value}%`;
}

export default function IncentivoCard({ incentivo, onPress }: IncentivoCardProps) {
  const handlePress = () => {
    if (onPress) onPress(incentivo);
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={handlePress}
      activeOpacity={0.7}
      accessibilityLabel={`Incentivo: ${incentivo.titolo}`}
    >
      <View style={styles.content}>
        {/* Tipo badge + Aliquota */}
        <View style={styles.header}>
          {incentivo.tipo && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{incentivo.tipo}</Text>
            </View>
          )}
          {incentivo.aliquota !== null && incentivo.aliquota !== undefined && (
            <View style={styles.aliquota}>
              <Ionicons name="pricetag" size={16} color={colors.green[700]} />
              <Text style={styles.aliquotaText}>{formatAliquota(incentivo.aliquota)}</Text>
            </View>
          )}
        </View>

        {/* Titolo */}
        <Text style={styles.title} numberOfLines={2}>
          {incentivo.titolo}
        </Text>

        {/* Descrizione */}
        {incentivo.descrizione && (
          <Text style={styles.description} numberOfLines={3}>
            {incentivo.descrizione}
          </Text>
        )}

        {/* Meta */}
        <View style={styles.meta}>
          {incentivo.ente_erogatore && (
            <View style={styles.metaItem}>
              <Ionicons name="business-outline" size={14} color={colors.slate[500]} />
              <Text style={styles.metaText} numberOfLines={1}>
                {incentivo.ente_erogatore.length > 30
                  ? incentivo.ente_erogatore.slice(0, 30) + '…'
                  : incentivo.ente_erogatore}
              </Text>
            </View>
          )}
          {incentivo.scadenza && (
            <View style={styles.metaItem}>
              <Ionicons name="calendar-outline" size={14} color={colors.slate[500]} />
              <Text style={styles.metaText}>Scade {formatDate(incentivo.scadenza)}</Text>
            </View>
          )}
        </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  badge: {
    backgroundColor: colors.green[100],
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.green[700],
  },
  aliquota: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  aliquotaText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.green[700],
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.slate[900],
    lineHeight: 22,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: colors.slate[600],
    lineHeight: 20,
    marginBottom: 10,
  },
  meta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.slate[100],
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: 12,
    color: colors.slate[500],
    maxWidth: 180,
  },
});
