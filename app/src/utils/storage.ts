// ============================================================
// EdilEngine - Storage (AsyncStorage)
// Persistenza locale per React Native
// ============================================================

import AsyncStorage from '@react-native-async-storage/async-storage';

const KEYS = {
  RECENT_SEARCHES: 'edilengine_recent_searches',
  CHAT_SESSION_ID: 'edilengine_chat_session',
  FAVORITES: 'edilengine_favorites',
} as const;

const MAX_RECENT_SEARCHES = 10;

// ============================================================
// Ricerche recenti
// ============================================================

export interface RecentSearch {
  query: string;
  timestamp: number;
}

export async function getRecentSearches(): Promise<RecentSearch[]> {
  try {
    const data = await AsyncStorage.getItem(KEYS.RECENT_SEARCHES);
    if (!data) return [];
    return JSON.parse(data) as RecentSearch[];
  } catch {
    return [];
  }
}

export async function addRecentSearch(query: string): Promise<void> {
  try {
    const searches = await getRecentSearches();
    // Remove duplicate
    const filtered = searches.filter((s) => s.query !== query);
    // Add to front
    filtered.unshift({ query, timestamp: Date.now() });
    // Limit
    const limited = filtered.slice(0, MAX_RECENT_SEARCHES);
    await AsyncStorage.setItem(KEYS.RECENT_SEARCHES, JSON.stringify(limited));
  } catch {
    // Silently fail
  }
}

export async function clearRecentSearches(): Promise<void> {
  try {
    await AsyncStorage.removeItem(KEYS.RECENT_SEARCHES);
  } catch {
    // Silently fail
  }
}

// ============================================================
// Sessione Chat
// ============================================================

export async function getChatSessionId(): Promise<string | null> {
  try {
    return await AsyncStorage.getItem(KEYS.CHAT_SESSION_ID);
  } catch {
    return null;
  }
}

export async function setChatSessionId(sessionId: string): Promise<void> {
  try {
    await AsyncStorage.setItem(KEYS.CHAT_SESSION_ID, sessionId);
  } catch {
    // Silently fail
  }
}

export async function clearChatSession(): Promise<void> {
  try {
    await AsyncStorage.removeItem(KEYS.CHAT_SESSION_ID);
  } catch {
    // Silently fail
  }
}

// ============================================================
// Preferiti
// ============================================================

export async function getFavorites(): Promise<string[]> {
  try {
    const data = await AsyncStorage.getItem(KEYS.FAVORITES);
    if (!data) return [];
    return JSON.parse(data) as string[];
  } catch {
    return [];
  }
}

export async function toggleFavorite(id: string): Promise<boolean> {
  try {
    const favorites = await getFavorites();
    const index = favorites.indexOf(id);
    if (index >= 0) {
      favorites.splice(index, 1);
      await AsyncStorage.setItem(KEYS.FAVORITES, JSON.stringify(favorites));
      return false;
    } else {
      favorites.push(id);
      await AsyncStorage.setItem(KEYS.FAVORITES, JSON.stringify(favorites));
      return true;
    }
  } catch {
    return false;
  }
}

export async function isFavorite(id: string): Promise<boolean> {
  try {
    const favorites = await getFavorites();
    return favorites.includes(id);
  } catch {
    return false;
  }
}
