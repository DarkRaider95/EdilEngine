// ============================================================
// EdilEngine - IncentiviScreen
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
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import IncentivoCard from '../components/IncentivoCard';
import { getIncentivi, ApiError } from '../services/api';
import type { IncentivoBase, IncentivoListResponse } from '../services/types';

type NavigationProp = any;

const TIPO_FILTERS = ['', 'Bonus fiscale', 'Contributo', 'Finanziamento agevolato', 'Detrazione', 'Esclusione'];
const ENTE_FILTERS = ['', 'Statale', 'Regionale', 'Comunale', 'UE', 'GSE'];

export default function IncentiviScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [incentivi, setIncentivi] = useState<IncentivoBase[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tipoFilter, setTipoFilter] = useState('');
  const [enteFilter, setEnteFilter] = useState('');
  const [showTipoFilter, setShowTipoFilter] = useState(false);
  const [showEnteFilter, setShowEnteFilter] = useState(false);

  const fetchIncentivi = useCallback(
    async (pageNum: number = 1, reset: boolean = false) => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string | number> = {
          page: pageNum,
          page_size: 20,
        };
        if (tipoFilter) params.tipo = tipoFilter;
        if (enteFilter) params.ente_erogatore = enteFilter;

        const data: IncentivoListResponse = await getIncentivi(params);
        if (reset) {
          setIncentivi(data.items);
        } else {
          setIncentivi((prev) => [...prev, ...data.items]);
        }
        setTotal(data.total);
        setPage(data.page);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Errore nel caricamento degli incentivi');
        }
      } finally {
        setLoading(false);
      }
    },
    [tipoFilter, enteFilter]
  );

  useEffect(() => {
    fetchIncentivi(1, true);
  }, [tipoFilter, enteFilter]);

  const handleIncentivoPress = (incentivo: IncentivoBase) => {
    if (incentivo.id) {
      navigation.navigate('IncentivoDetail', { id: incentivo.id });
    }
  };

  const handleLoadMore = () => {
    if (loading || incentivi.length >= total) return;
    fetchIncentivi(page + 1, false);
  };

  const renderItem = ({ item }: { item: IncentivoBase }) => (
    <IncentivoCard incentivo={item} onPress={handleIncentivoPress} />
  );

  const renderFooter = () => {
    if (loading) {
      return (
        <View style={styles.footer}>
          <ActivityIndicator color={colors.primary[600]} size="small" />
          <Text style={styles.footerText}>Caricamento...</Text>
        </View>
      );
    }
    if (incentivi.length < total) {
      return (
        <TouchableOpacity style={styles.loadMoreButton} onPress={handleLoadMore}>
          <Text style={styles.loadMoreText}>Carica altro</Text>
        </TouchableOpacity>
      );
    }
    return <View style={{ height: 24 }} />;
  };

  const renderEmpty = () => {
    if (loading) return null;
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="pricetag-outline" size={48} color={colors.slate[300]} />
        <Text style={styles.emptyText}>Nessun incentivo trovato</Text>
        <Text style={styles.emptySubtext}>Prova a modificare i filtri</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Filters */}
      <View style={styles.filtersContainer}>
        <View style={styles.filterRow}>
          {/* Tipo filter */}
          <View style={styles.filterWrapper}>
            <TouchableOpacity
              style={styles.filterButton}
              onPress={() => {
                setShowTipoFilter(!showTipoFilter);
                setShowEnteFilter(false);
              }}
            >
              <Ionicons name="filter-outline" size={16} color={colors.slate[600]} />
              <Text style={styles.filterButtonText}>
                {tipoFilter || 'Tipo'}
              </Text>
              <Ionicons name="chevron-down" size={14} color={colors.slate[400]} />
            </TouchableOpacity>
            {showTipoFilter && (
              <View style={styles.filterDropdown}>
                {TIPO_FILTERS.map((f) => (
                  <TouchableOpacity
                    key={f}
                    style={[styles.filterOption, tipoFilter === f && styles.filterOptionActive]}
                    onPress={() => {
                      setTipoFilter(f);
                      setShowTipoFilter(false);
                    }}
                  >
                    <Text style={[styles.filterOptionText, tipoFilter === f && styles.filterOptionTextActive]}>
                      {f || 'Tutti'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>

          {/* Ente filter */}
          <View style={styles.filterWrapper}>
            <TouchableOpacity
              style={styles.filterButton}
              onPress={() => {
                setShowEnteFilter(!showEnteFilter);
                setShowTipoFilter(false);
              }}
            >
              <Ionicons name="business-outline" size={16} color={colors.slate[600]} />
              <Text style={styles.filterButtonText}>
                {enteFilter || 'Ente'}
              </Text>
              <Ionicons name="chevron-down" size={14} color={colors.slate[400]} />
            </TouchableOpacity>
            {showEnteFilter && (
              <View style={styles.filterDropdown}>
                {ENTE_FILTERS.map((f) => (
                  <TouchableOpacity
                    key={f}
                    style={[styles.filterOption, enteFilter === f && styles.filterOptionActive]}
                    onPress={() => {
                      setEnteFilter(f);
                      setShowEnteFilter(false);
                    }}
                  >
                    <Text style={[styles.filterOptionText, enteFilter === f && styles.filterOptionTextActive]}>
                      {f || 'Tutti'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>

          {total > 0 && (
            <Text style={styles.resultCount}>
              {total} {total === 1 ? 'incentivo' : 'incentivi'}
            </Text>
          )}
        </View>
      </View>

      {/* Error */}
      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={18} color={colors.error} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* List */}
      <FlatList
        data={incentivi}
        keyExtractor={(item, index) => item.id || `inc-${index}`}
        renderItem={renderItem}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  filtersContainer: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  filterRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    flexWrap: 'wrap',
  },
  filterWrapper: {
    position: 'relative',
    zIndex: 10,
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  filterButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: colors.slate[700],
  },
  filterDropdown: {
    position: 'absolute',
    top: 42,
    left: 0,
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.slate[200],
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    minWidth: 180,
    zIndex: 20,
  },
  filterOption: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.slate[100],
  },
  filterOptionActive: {
    backgroundColor: colors.primary[50],
  },
  filterOptionText: {
    fontSize: 14,
    color: colors.slate[700],
  },
  filterOptionTextActive: {
    color: colors.primary[700],
    fontWeight: '600',
  },
  resultCount: {
    marginLeft: 'auto',
    fontSize: 13,
    color: colors.slate[500],
    alignSelf: 'center',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 12,
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
});
