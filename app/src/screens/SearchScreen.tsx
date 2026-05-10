// ============================================================
// EdilEngine - SearchScreen
// ============================================================

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import SearchBar from '../components/SearchBar';
import LeggeCard from '../components/LeggeCard';
import { useSearch } from '../hooks/useSearch';
import type { LeggeBase, SemanticSearchResult } from '../services/types';

type NavigationProp = any;
type RouteProp = any;

export default function SearchScreen() {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProp>();
  const {
    results,
    total,
    loading,
    error,
    isSemantic,
    search,
    semanticSearchFn,
    loadMore,
    clearResults,
  } = useSearch();

  const [mode, setMode] = useState<'text' | 'semantic'>('text');
  const [currentQuery, setCurrentQuery] = useState('');

  // Handle incoming query from navigation params
  useEffect(() => {
    const query = route.params?.query;
    if (query) {
      setCurrentQuery(query);
      handleSearch(query, mode);
    }
  }, [route.params?.query]);

  const handleSearch = useCallback(
    (query: string, searchMode: 'text' | 'semantic' = mode) => {
      setCurrentQuery(query);
      if (searchMode === 'semantic') {
        semanticSearchFn(query);
      } else {
        search(query);
      }
    },
    [mode, search, semanticSearchFn]
  );

  const handleModeChange = (newMode: 'text' | 'semantic') => {
    setMode(newMode);
    if (currentQuery) {
      if (newMode === 'semantic') {
        semanticSearchFn(currentQuery);
      } else {
        search(currentQuery);
      }
    }
  };

  const handleLeggePress = (legge: LeggeBase | SemanticSearchResult) => {
    if ('legge_id' in legge) {
      // SemanticSearchResult
      navigation.navigate('LeggeDetail', { id: legge.legge_id });
    } else if (legge.id) {
      navigation.navigate('LeggeDetail', { id: legge.id });
    }
  };

  const handleChatPress = (legge: LeggeBase | SemanticSearchResult) => {
    const titolo = 'legge_titolo' in legge ? legge.legge_titolo : legge.titolo;
    navigation.navigate('Chat', { initialMessage: `Cosa mi dici su "${titolo}"?` });
  };

  const canLoadMore = !isSemantic && results.length < total;

  const renderItem = ({ item }: { item: LeggeBase | SemanticSearchResult }) => {
    if ('legge_id' in item) {
      // SemanticSearchResult
      const sr = item as SemanticSearchResult;
      const leggeBase: LeggeBase = {
        id: sr.legge_id,
        titolo: sr.legge_titolo || '',
        tipo: sr.legge_tipo || null,
        numero: sr.legge_numero || null,
        data_emanazione: null,
        data_pubblicazione: null,
        data_vigore: null,
        autorita: null,
        url_fonte: sr.legge_url_fonte || null,
      };
      return (
        <View>
          <LeggeCard
            legge={leggeBase}
            onPress={() => handleLeggePress(item)}
            onChatPress={() => handleChatPress(item)}
          />
          <Text style={styles.similarityText}>
            Rilevanza: {(sr.similarity * 100).toFixed(1)}%
          </Text>
          {sr.chunk_text && (
            <Text style={styles.chunkText} numberOfLines={3}>
              &ldquo;{sr.chunk_text}&rdquo;
            </Text>
          )}
        </View>
      );
    }
    // Regular LeggeBase
    return (
      <LeggeCard
        legge={item as LeggeBase}
        onPress={() => handleLeggePress(item)}
        onChatPress={() => handleChatPress(item)}
      />
    );
  };

  const renderFooter = () => {
    if (loading) {
      return (
        <View style={styles.footer}>
          <ActivityIndicator color={colors.primary[600]} size="small" />
          <Text style={styles.footerText}>Caricamento...</Text>
        </View>
      );
    }
    if (canLoadMore) {
      return (
        <TouchableOpacity style={styles.loadMoreButton} onPress={loadMore}>
          <Text style={styles.loadMoreText}>Carica altro</Text>
        </TouchableOpacity>
      );
    }
    return null;
  };

  const renderEmpty = () => {
    if (loading) return null;
    if (error) {
      return (
        <View style={styles.emptyContainer}>
          <Ionicons name="alert-circle-outline" size={48} color={colors.error} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      );
    }
    if (currentQuery) {
      return (
        <View style={styles.emptyContainer}>
          <Ionicons name="search-outline" size={48} color={colors.slate[300]} />
          <Text style={styles.emptyText}>Nessun risultato trovato</Text>
          <Text style={styles.emptySubtext}>Prova con altri termini di ricerca</Text>
        </View>
      );
    }
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="search-outline" size={48} color={colors.slate[300]} />
        <Text style={styles.emptyText}>Cerca leggi e decreti</Text>
        <Text style={styles.emptySubtext}>
          Usa la barra di ricerca per trovare normative edilizie
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <SearchBar
          defaultValue={currentQuery}
          onSearch={(q) => handleSearch(q)}
          placeholder="Cerca leggi, decreti..."
        />
      </View>

      {/* Toggle mode */}
      <View style={styles.toggleContainer}>
        <TouchableOpacity
          style={[styles.toggleButton, mode === 'text' && styles.toggleButtonActive]}
          onPress={() => handleModeChange('text')}
        >
          <Ionicons
            name="text-outline"
            size={16}
            color={mode === 'text' ? colors.white : colors.slate[500]}
          />
          <Text style={[styles.toggleText, mode === 'text' && styles.toggleTextActive]}>
            Testo
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.toggleButton, mode === 'semantic' && styles.toggleButtonActive]}
          onPress={() => handleModeChange('semantic')}
        >
          <Ionicons
            name="sparkles-outline"
            size={16}
            color={mode === 'semantic' ? colors.white : colors.slate[500]}
          />
          <Text style={[styles.toggleText, mode === 'semantic' && styles.toggleTextActive]}>
            Semantico
          </Text>
        </TouchableOpacity>
        {total > 0 && (
          <Text style={styles.resultCount}>
            {total} {total === 1 ? 'risultato' : 'risultati'}
          </Text>
        )}
      </View>

      {/* Results */}
      <FlatList
        data={results}
        keyExtractor={(item, index) => `${'legge_id' in item ? item.legge_id : (item as LeggeBase).id || index}`}
        renderItem={renderItem}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  toggleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 12,
    gap: 8,
  },
  toggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: colors.slate[100],
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  toggleButtonActive: {
    backgroundColor: colors.primary[600],
    borderColor: colors.primary[600],
  },
  toggleText: {
    fontSize: 13,
    fontWeight: '500',
    color: colors.slate[500],
  },
  toggleTextActive: {
    color: colors.white,
  },
  resultCount: {
    marginLeft: 'auto',
    fontSize: 13,
    color: colors.slate[500],
  },
  list: {
    paddingHorizontal: 16,
    flexGrow: 1,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
  },
  footerText: {
    fontSize: 14,
    color: colors.slate[500],
  },
  loadMoreButton: {
    alignItems: 'center',
    paddingVertical: 16,
    marginBottom: 24,
  },
  loadMoreText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.primary[600],
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
    paddingTop: 80,
  },
  emptyText: {
    fontSize: 17,
    fontWeight: '600',
    color: colors.slate[600],
    marginTop: 16,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.slate[400],
    marginTop: 8,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 15,
    color: colors.error,
    marginTop: 16,
    textAlign: 'center',
  },
  similarityText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.primary[600],
    marginTop: -8,
    marginBottom: 4,
    paddingLeft: 4,
  },
  chunkText: {
    fontSize: 13,
    color: colors.slate[500],
    fontStyle: 'italic',
    marginTop: -4,
    marginBottom: 12,
    paddingLeft: 4,
    lineHeight: 18,
  },
});
