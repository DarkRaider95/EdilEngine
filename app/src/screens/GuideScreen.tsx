// ============================================================
// EdilEngine - GuideScreen
// ============================================================

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import GuideForm from '../components/GuideForm';
import { useGuide } from '../hooks/useGuide';
import type { GuideResponse } from '../services/types';

export default function GuideScreen() {
  const { result, loading, error, submitGuide, clearResult } = useGuide();

  if (result) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.resultContent}>
        {/* Header */}
        <View style={styles.resultHeader}>
          <Ionicons name="checkmark-circle" size={40} color={colors.green[500]} />
          <Text style={styles.resultTitle}>Guida Personalizzata</Text>
          <Text style={styles.resultSubtitle}>
            Ecco cosa devi sapere per il tuo progetto
          </Text>
        </View>

        {/* Vincoli */}
        {result.vincoli && result.vincoli.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="lock-closed-outline" size={20} color={colors.slate[700]} />
              <Text style={styles.sectionTitle}>Vincoli normativi</Text>
            </View>
            {result.vincoli.map((v, i) => (
              <View key={v.id || i} style={styles.card}>
                {v.descrizione && (
                  <Text style={styles.cardText}>{v.descrizione}</Text>
                )}
                {v.norma_riferimento && (
                  <Text style={styles.cardNorma}>
                    Norma di riferimento: {v.norma_riferimento}
                  </Text>
                )}
                <Text style={styles.cardLocation}>
                  {[v.regione, v.provincia, v.comune, v.tipo_zona]
                    .filter(Boolean)
                    .join(' · ')}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Incentivi */}
        {result.incentivi && result.incentivi.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="pricetag-outline" size={20} color={colors.slate[700]} />
              <Text style={styles.sectionTitle}>Incentivi disponibili</Text>
            </View>
            {result.incentivi.map((inc, i) => (
              <View key={inc.id || i} style={styles.card}>
                <Text style={styles.cardTitle}>{inc.titolo}</Text>
                {inc.descrizione && (
                  <Text style={styles.cardText}>{inc.descrizione}</Text>
                )}
                {inc.aliquota !== null && (
                  <Text style={styles.cardAliquota}>Aliquota: {inc.aliquota}%</Text>
                )}
              </View>
            ))}
          </View>
        )}

        {/* Checklist */}
        {result.checklist && result.checklist.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="checkbox-outline" size={20} color={colors.slate[700]} />
              <Text style={styles.sectionTitle}>Checklist</Text>
            </View>
            <View style={styles.checklistContainer}>
              {result.checklist.map((item, i) => (
                <View key={i} style={styles.checklistItem}>
                  <Ionicons name="checkmark-circle" size={18} color={colors.green[500]} />
                  <Text style={styles.checklistText}>{item}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Nuova guida */}
        <TouchableOpacity style={styles.newButton} onPress={clearResult}>
          <Ionicons name="refresh-outline" size={18} color={colors.primary[600]} />
          <Text style={styles.newButtonText}>Nuova guida</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  return (
    <View style={styles.container}>
      {/* Error */}
      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={16} color={colors.error} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Loading overlay */}
      {loading && (
        <View style={styles.loadingOverlay}>
          <View style={styles.loadingCard}>
            <ActivityIndicator size="large" color={colors.primary[600]} />
            <Text style={styles.loadingTitle}>Generazione in corso...</Text>
            <Text style={styles.loadingText}>
              Stiamo analizzando la normativa per la tua zona
            </Text>
          </View>
        </View>
      )}

      <ScrollView contentContainerStyle={styles.formContent}>
        <View style={styles.intro}>
          <Ionicons name="compass-outline" size={36} color={colors.primary[600]} />
          <Text style={styles.introTitle}>Guida Personalizzata</Text>
          <Text style={styles.introText}>
            Compila il form per ottenere una guida completa su vincoli, permessi e
            incentivi per il tuo progetto edilizio.
          </Text>
        </View>

        <GuideForm onSubmit={submitGuide} loading={loading} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  formContent: {
    paddingBottom: 40,
  },
  intro: {
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 8,
  },
  introTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.slate[900],
    marginTop: 10,
    marginBottom: 8,
  },
  introText: {
    fontSize: 14,
    color: colors.slate[500],
    textAlign: 'center',
    lineHeight: 20,
  },
  resultContent: {
    padding: 16,
    paddingBottom: 40,
  },
  resultHeader: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  resultTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.slate[900],
    marginTop: 10,
  },
  resultSubtitle: {
    fontSize: 14,
    color: colors.slate[500],
    marginTop: 4,
    textAlign: 'center',
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: colors.slate[800],
  },
  card: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.slate[200],
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.slate[900],
    marginBottom: 6,
  },
  cardText: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.slate[700],
    marginBottom: 4,
  },
  cardNorma: {
    fontSize: 12,
    color: colors.slate[500],
    fontStyle: 'italic',
    marginTop: 4,
  },
  cardLocation: {
    fontSize: 12,
    color: colors.slate[400],
    marginTop: 6,
  },
  cardAliquota: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.green[700],
    marginTop: 4,
  },
  checklistContainer: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.slate[200],
    gap: 10,
  },
  checklistItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  checklistText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
    color: colors.slate[700],
  },
  newButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
    marginTop: 8,
  },
  newButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.primary[600],
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginHorizontal: 16,
    marginTop: 8,
    padding: 10,
    backgroundColor: '#fef2f2',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  errorText: {
    flex: 1,
    fontSize: 13,
    color: colors.error,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.3)',
    zIndex: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingCard: {
    backgroundColor: colors.white,
    borderRadius: 20,
    padding: 30,
    marginHorizontal: 32,
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
  },
  loadingTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: colors.slate[900],
    marginTop: 16,
  },
  loadingText: {
    fontSize: 14,
    color: colors.slate[500],
    marginTop: 6,
    textAlign: 'center',
  },
});
