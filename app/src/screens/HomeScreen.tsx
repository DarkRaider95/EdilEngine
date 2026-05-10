// ============================================================
// EdilEngine - HomeScreen
// ============================================================

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';
import SearchBar from '../components/SearchBar';
import { getRecentSearches, type RecentSearch } from '../utils/storage';

type NavigationProp = any;

export default function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadRecentSearches = useCallback(async () => {
    const searches = await getRecentSearches();
    setRecentSearches(searches);
  }, []);

  useEffect(() => {
    loadRecentSearches();
  }, [loadRecentSearches]);

  // Refresh when screen is focused
  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadRecentSearches();
    });
    return unsubscribe;
  }, [navigation, loadRecentSearches]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadRecentSearches();
    setRefreshing(false);
  }, [loadRecentSearches]);

  const handleSearch = (query: string) => {
    navigation.navigate('Cerca', { query });
  };

  const handleRecentSearchPress = (search: RecentSearch) => {
    navigation.navigate('Cerca', { query: search.query });
  };

  const quickActions = [
    {
      title: 'Cerca Leggi',
      subtitle: 'Cerca tra le leggi edilizie',
      icon: 'search' as const,
      color: colors.primary[600],
      bgColor: colors.primary[50],
      route: 'Cerca',
    },
    {
      title: 'Incentivi',
      subtitle: 'Scopri bonus e agevolazioni',
      icon: 'pricetag' as const,
      color: colors.green[600],
      bgColor: colors.green[50],
      route: 'Incentivi',
    },
    {
      title: 'Guida Personalizzata',
      subtitle: 'Ottieni la tua guida normativa',
      icon: 'compass' as const,
      color: '#7c3aed',
      bgColor: '#f5f3ff',
      route: 'Guida',
    },
    {
      title: 'Chatbot RAG',
      subtitle: 'Parla con il nostro assistente AI',
      icon: 'chatbubble-ellipses' as const,
      color: '#0891b2',
      bgColor: '#ecfeff',
      route: 'Chat',
    },
  ];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary[600]]} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.appName}>EdilEngine</Text>
        <Text style={styles.tagline}>Naviga le leggi italiane dell&apos;edilizia</Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <SearchBar
          placeholder="Cerca leggi, decreti..."
          onSearch={handleSearch}
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cosa vuoi fare?</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.quickActionCard}
              onPress={() => navigation.navigate(action.route)}
              activeOpacity={0.7}
            >
              <View style={[styles.quickActionIcon, { backgroundColor: action.bgColor }]}>
                <Ionicons name={action.icon} size={26} color={action.color} />
              </View>
              <Text style={styles.quickActionTitle}>{action.title}</Text>
              <Text style={styles.quickActionSubtitle}>{action.subtitle}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Searches */}
      {recentSearches.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ricerche recenti</Text>
          {recentSearches.map((search, index) => (
            <TouchableOpacity
              key={index}
              style={styles.recentItem}
              onPress={() => handleRecentSearchPress(search)}
            >
              <Ionicons name="time-outline" size={18} color={colors.slate[400]} />
              <Text style={styles.recentText} numberOfLines={1}>
                {search.query}
              </Text>
              <Ionicons name="chevron-forward" size={16} color={colors.slate[300]} />
            </TouchableOpacity>
          ))}
        </View>
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
    paddingBottom: 40,
  },
  header: {
    paddingTop: 16,
    paddingHorizontal: 20,
    paddingBottom: 8,
  },
  appName: {
    fontSize: 28,
    fontWeight: '800',
    color: colors.primary[600],
    letterSpacing: -0.5,
  },
  tagline: {
    fontSize: 14,
    color: colors.slate[500],
    marginTop: 2,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  section: {
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.slate[800],
    marginBottom: 14,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  quickActionCard: {
    width: '47%',
    backgroundColor: colors.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.slate[200],
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  quickActionIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  quickActionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.slate[900],
    marginBottom: 4,
  },
  quickActionSubtitle: {
    fontSize: 12,
    color: colors.slate[500],
    lineHeight: 16,
  },
  recentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 12,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: colors.slate[100],
  },
  recentText: {
    flex: 1,
    fontSize: 15,
    color: colors.slate[700],
  },
});
