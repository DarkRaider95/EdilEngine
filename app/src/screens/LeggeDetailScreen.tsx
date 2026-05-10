// ============================================================
// EdilEngine - LeggeDetailScreen
// ============================================================

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { getLegge, ApiError } from '../services/api';
import type { LeggeDetail } from '../services/types';

type RouteProp = any;
type NavigationProp = any;

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

export default function LeggeDetailScreen() {
  const route = useRoute<RouteProp>();
  const navigation = useNavigation<NavigationProp>();
  const { id } = route.params as { id: string };

  const [legge, setLegge] = useState<LeggeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLegge = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getLegge(id);
        setLegge(data);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Errore nel caricamento della legge');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchLegge();
  }, [id]);

  const handleChatPress = () => {
    if (legge) {
      navigation.navigate('Chat', {
        initialMessage: `Cosa mi dici sulla legge "${legge.titolo}"?`,
      });
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary[600]} />
        <Text style={styles.loadingText}>Caricamento...</Text>
      </View>
    );
  }

  if (error || !legge) {
    return (
      <View style={styles.centered}>
        <Ionicons name="alert-circle-outline" size={48} color={colors.error} />
        <Text style={styles.errorText}>{error || 'Legge non trovata'}</Text>
      </View>
    );
  }

  const badgeStyle = getTipoBadgeStyle(legge.tipo);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Tipo badge */}
      {legge.tipo && (
        <View style={[styles.badge, { backgroundColor: badgeStyle.bg }]}>
          <Text style={[styles.badgeText, { color: badgeStyle.text }]}>{legge.tipo}</Text>
        </View>
      )}

      {/* Titolo */}
      <Text style={styles.title}>{legge.titolo}</Text>

      {/* Meta info */}
      <View style={styles.metaGrid}>
        {legge.numero && (
          <View style={styles.metaItem}>
            <Ionicons name="document-text-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Numero</Text>
            <Text style={styles.metaValue}>{legge.numero}</Text>
          </View>
        )}
        {legge.data_emanazione && (
          <View style={styles.metaItem}>
            <Ionicons name="calendar-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Emanazione</Text>
            <Text style={styles.metaValue}>{formatDate(legge.data_emanazione)}</Text>
          </View>
        )}
        {legge.data_pubblicazione && (
          <View style={styles.metaItem}>
            <Ionicons name="newspaper-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Pubblicazione</Text>
            <Text style={styles.metaValue}>{formatDate(legge.data_pubblicazione)}</Text>
          </View>
        )}
        {legge.data_vigore && (
          <View style={styles.metaItem}>
            <Ionicons name="checkmark-circle-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>In vigore</Text>
            <Text style={styles.metaValue}>{formatDate(legge.data_vigore)}</Text>
          </View>
        )}
        {legge.autorita && (
          <View style={styles.metaItem}>
            <Ionicons name="business-outline" size={16} color={colors.slate[500]} />
            <Text style={styles.metaLabel}>Autorità</Text>
            <Text style={styles.metaValue}>{legge.autorita}</Text>
          </View>
        )}
      </View>

      {/* Categorie */}
      {legge.categorie && legge.categorie.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Categorie</Text>
          <View style={styles.categorieContainer}>
            {legge.categorie.map((cat) => (
              <View key={cat.id} style={styles.categoriaBadge}>
                <Text style={styles.categoriaText}>{cat.nome}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* URL Fonte */}
      {legge.url_fonte && (
        <TouchableOpacity
          style={styles.linkButton}
          onPress={() => Linking.openURL(legge.url_fonte!)}
        >
          <Ionicons name="link-outline" size={16} color={colors.primary[600]} />
          <Text style={styles.linkText}>Vai alla fonte originale</Text>
        </TouchableOpacity>
      )}

      {/* Testo completo */}
      {legge.testo_completo && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Testo completo</Text>
          <View style={styles.testoContainer}>
            <Text style={styles.testoText}>{legge.testo_completo}</Text>
          </View>
        </View>
      )}

      {/* Chat button */}
      <TouchableOpacity style={styles.chatButton} onPress={handleChatPress}>
        <Ionicons name="chatbubble-ellipses-outline" size={20} color={colors.white} />
        <Text style={styles.chatButtonText}>Chiedi al chatbot</Text>
      </TouchableOpacity>
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
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 20,
    marginBottom: 12,
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '600',
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
    width: 90,
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
  categorieContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoriaBadge: {
    backgroundColor: colors.primary[50],
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
  },
  categoriaText: {
    fontSize: 13,
    fontWeight: '500',
    color: colors.primary[700],
  },
  linkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 20,
    paddingVertical: 10,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.primary[600],
  },
  testoContainer: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  testoText: {
    fontSize: 15,
    lineHeight: 24,
    color: colors.slate[800],
  },
  chatButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    backgroundColor: colors.primary[600],
    borderRadius: 14,
    paddingVertical: 15,
    marginTop: 8,
    shadowColor: colors.primary[600],
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  chatButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
});
