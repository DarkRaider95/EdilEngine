// ============================================================
// EdilEngine - SearchBar Component
// ============================================================

import React, { useState, useCallback } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Keyboard,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';

interface SearchBarProps {
  placeholder?: string;
  defaultValue?: string;
  onSearch?: (query: string) => void;
  autoFocus?: boolean;
}

export default function SearchBar({
  placeholder = 'Cerca leggi, decreti...',
  defaultValue = '',
  onSearch,
  autoFocus = false,
}: SearchBarProps) {
  const [query, setQuery] = useState(defaultValue);

  const handleSearch = useCallback(() => {
    const trimmed = query.trim();
    if (!trimmed) return;
    Keyboard.dismiss();
    if (onSearch) {
      onSearch(trimmed);
    }
  }, [query, onSearch]);

  return (
    <View style={styles.container}>
      <View style={styles.inputWrapper}>
        <Ionicons
          name="search"
          size={20}
          color={colors.slate[400]}
          style={styles.icon}
        />
        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={handleSearch}
          placeholder={placeholder}
          placeholderTextColor={colors.slate[400]}
          returnKeyType="search"
          autoFocus={autoFocus}
          autoCorrect={false}
          accessibilityLabel="Cerca leggi"
        />
        {query.length > 0 && (
          <TouchableOpacity
            onPress={() => setQuery('')}
            style={styles.clearButton}
            accessibilityLabel="Cancella ricerca"
          >
            <Ionicons name="close-circle" size={18} color={colors.slate[400]} />
          </TouchableOpacity>
        )}
      </View>
      <TouchableOpacity
        style={styles.button}
        onPress={handleSearch}
        accessibilityLabel="Esegui ricerca"
      >
        <Ionicons name="search" size={20} color={colors.white} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 10,
    alignItems: 'center',
  },
  inputWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.slate[300],
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  icon: {
    paddingLeft: 14,
  },
  input: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 10,
    fontSize: 16,
    color: colors.slate[900],
  },
  clearButton: {
    paddingRight: 12,
    paddingLeft: 4,
  },
  button: {
    backgroundColor: colors.primary[600],
    borderRadius: 14,
    padding: 13,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary[600],
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
});
