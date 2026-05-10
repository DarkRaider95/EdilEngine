// ============================================================
// EdilEngine - ProfileScreen
// ============================================================

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { clearRecentSearches, clearChatSession } from '../utils/storage';

export default function ProfileScreen() {
  const [cleared, setCleared] = useState(false);

  const handleClearRecentSearches = () => {
    Alert.alert(
      'Cancella ricerche recenti',
      'Sei sicuro di voler cancellare tutte le ricerche recenti?',
      [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Cancella',
          style: 'destructive',
          onPress: async () => {
            await clearRecentSearches();
            setCleared(true);
            setTimeout(() => setCleared(false), 2000);
          },
        },
      ]
    );
  };

  const handleClearChatSession = () => {
    Alert.alert(
      'Cancella sessione chat',
      'Sei sicuro di voler cancellare la sessione chat corrente?',
      [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Cancella',
          style: 'destructive',
          onPress: async () => {
            await clearChatSession();
            setCleared(true);
            setTimeout(() => setCleared(false), 2000);
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* App info header */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Ionicons name="construct-outline" size={40} color={colors.primary[600]} />
        </View>
        <Text style={styles.appName}>EdilEngine</Text>
        <Text style={styles.version}>Versione 1.0.0</Text>
        <Text style={styles.description}>
          Naviga le leggi italiane dell&apos;edilizia con il nostro assistente AI.
        </Text>
      </View>

      {/* Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Gestione dati</Text>

        <TouchableOpacity style={styles.actionItem} onPress={handleClearRecentSearches}>
          <View style={[styles.actionIcon, { backgroundColor: colors.warning + '20' }]}>
            <Ionicons name="time-outline" size={20} color={colors.warning} />
          </View>
          <View style={styles.actionContent}>
            <Text style={styles.actionTitle}>Cancella ricerche recenti</Text>
            <Text style={styles.actionSubtitle}>Rimuovi la cronologia delle ricerche</Text>
          </View>
          <Ionicons name="chevron-forward" size={18} color={colors.slate[300]} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionItem} onPress={handleClearChatSession}>
          <View style={[styles.actionIcon, { backgroundColor: colors.error + '20' }]}>
            <Ionicons name="chatbubble-outline" size={20} color={colors.error} />
          </View>
          <View style={styles.actionContent}>
            <Text style={styles.actionTitle}>Cancella sessione chat</Text>
            <Text style={styles.actionSubtitle}>Avvia una nuova conversazione</Text>
          </View>
          <Ionicons name="chevron-forward" size={18} color={colors.slate[300]} />
        </TouchableOpacity>

        {cleared && (
          <View style={styles.successMessage}>
            <Ionicons name="checkmark-circle" size={16} color={colors.green[600]} />
            <Text style={styles.successText}>Dati cancellati con successo</Text>
          </View>
        )}
      </View>

      {/* Info section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informazioni</Text>

        <View style={styles.infoItem}>
          <Ionicons name="shield-checkmark-outline" size={20} color={colors.slate[500]} />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Privacy & Termini</Text>
            <Text style={styles.infoText}>
              I tuoi dati sono trattati nel rispetto della normativa GDPR.
            </Text>
          </View>
        </View>

        <View style={styles.infoItem}>
          <Ionicons name="server-outline" size={20} color={colors.slate[500]} />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Backend API</Text>
            <Text style={styles.infoText}>
              FastAPI con Retrieval Augmented Generation (RAG)
            </Text>
          </View>
        </View>

        <View style={styles.infoItem}>
          <Ionicons name="leaf-outline" size={20} color={colors.slate[500]} />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Tecnologia</Text>
            <Text style={styles.infoText}>
              React Native + Expo · Python FastAPI · ChromaDB · LLM
            </Text>
          </View>
        </View>
      </View>

      {/* Footer */}
      <Text style={styles.footer}>
        EdilEngine © 2026 · Tutti i diritti riservati
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  content: {
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 30,
    paddingHorizontal: 24,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 24,
    backgroundColor: colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  appName: {
    fontSize: 26,
    fontWeight: '800',
    color: colors.primary[600],
    letterSpacing: -0.5,
  },
  version: {
    fontSize: 13,
    color: colors.slate[400],
    marginTop: 4,
  },
  description: {
    fontSize: 14,
    color: colors.slate[500],
    textAlign: 'center',
    lineHeight: 20,
    marginTop: 12,
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.slate[500],
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
    paddingLeft: 4,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  actionIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.slate[900],
    marginBottom: 2,
  },
  actionSubtitle: {
    fontSize: 13,
    color: colors.slate[500],
  },
  successMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 4,
  },
  successText: {
    fontSize: 13,
    color: colors.green[600],
    fontWeight: '500',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.slate[100],
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.slate[800],
    marginBottom: 2,
  },
  infoText: {
    fontSize: 13,
    color: colors.slate[500],
    lineHeight: 18,
  },
  footer: {
    fontSize: 12,
    color: colors.slate[400],
    textAlign: 'center',
    marginTop: 8,
  },
});
