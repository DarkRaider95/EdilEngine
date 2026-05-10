// ============================================================
// EdilEngine - IncentivoDetailScreen
// ============================================================

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Linking,
  TouchableOpacity,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { getIncentivo, ApiError } from '../services/api';
import type { IncentivoDetail } from '../services/types';

type RouteProp = any;

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

export default function IncentivoDetailScreen() {
  const route = useRoute<RouteProp>();
  const { id } = route.params as { id: string };

  const [incentivo, setIncentivo] = useState<IncentivoDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncentivo = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getIncentivo(id);
        setIncentivo(data);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Errore nel caricamento dell\'incentivo');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchIncentivo();
  }, [id]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary[600]} />
        <Text style={styles.loadingText}>Caricamento...</Text>
      </View>
    );
  }

  if (error || !incentivo) {
    return (
      <View style={styles.centered}>
        <Ionicons name="alert-circle-outline" size={48} color={colors.error} />
        <Text style={styles.errorText}>{error || 'Incentivo non trovato'}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Tipo badge + Aliquota */}
      <View style={styles.header}>
        {incentivo.tipo && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{incentivo.tipo}</Text>
          </View>
        )}
        {incentivo.aliquota !== null && incentivo.aliquota !== undefined && (
          <View style={styles.aliquotaContainer}>
            <Ionicons name="pricetag" size={22} color={colors.green[700]} />
            <Text style={styles.aliquotaText}>{formatAliquota(incentivo.aliquota)}</Text>
          </View>
        )}
      </View>

      {/* Titolo */}
      <Text style={styles.title}>{incentivo.titolo}</Text>

      {/* Meta */}
      <View style={styles.metaGrid}>
        {incentivo.ente_erogatore && (
          <View style={styles.metaItem}>
            <Ionicons name="business-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Ente erogatore</Text>
            <Text style={styles.metaValue}>{incentivo.ente_erogatore}</Text>
          </View>
        )}
        {incentivo.scadenza && (
          <View style={styles.metaItem}>
            <Ionicons name="calendar-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Scadenza</Text>
            <Text style={styles.metaValue}>{formatDate(incentivo.scadenza)}</Text>
          </View>
        )}
      </View>

      {/* Descrizione */}
      {incentivo.descrizione && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Descrizione</Text>
          <View style={styles.textContainer}>
            <Text style={styles.bodyText}>{incentivo.descrizione}</Text>
          </View>
        </View>
      )}

      {/* Requisiti */}
      {incentivo.requisiti && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Requisiti</Text>
          <View style={styles.textContainer}>
            <Text style={styles.bodyText}>{incentivo.requisiti}</Text>
          </View>
        </View>
      )}

      {/* URL Fonte */}
      {incentivo.url_fonte && (
        <TouchableOpacity
          style={styles.linkButton}
          onPress={() => Linking.openURL(incentivo.url_fonte!)}
        >
          <Ionicons name="link-outline" size={16} color={colors.primary[600]} />
          <Text style={styles.linkText}>Vai alla fonte originale</Text>
        </TouchableOpacity>
      )}

      {/* Data creazione */}
      {incentivo.created_at && (
        <Text style={styles.createdAt}>
          Inserito il {formatDate(incentivo.created_at)}
        </Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.slate[50],
    padding: 24,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: colors.slate[500],
  },
  errorText: {
    marginTop: 12,
    fontSize: 15,
    color: colors.error,
    textAlign: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  badge: {
    backgroundColor: colors.green[100],
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.green[700],
  },
  aliquotaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.green[50],
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
  },
  aliquotaText: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.green[700],
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.slate[900],
    lineHeight: 30,
    marginBottom: 18,
  },
  metaGrid: {
    gap: 10,
    marginBottom: 20,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: colors.white,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  metaLabel: {
    fontSize: 13,
    color: colors.slate[500],
    width: 110,
  },
  metaValue: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
    color: colors.slate[800],
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: colors.slate[800],
    marginBottom: 10,
  },
  textContainer: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  bodyText: {
    fontSize: 15,
    lineHeight: 24,
    color: colors.slate[800],
  },
  linkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 16,
    paddingVertical: 10,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.primary[600],
  },
  createdAt: {
    fontSize: 12,
    color: colors.slate[400],
    textAlign: 'center',
    marginTop: 12,
  },
});
