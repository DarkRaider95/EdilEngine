// ============================================================
// EdilEngine - ChatScreen
// ============================================================

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import ChatBubble from '../components/ChatBubble';
import { useChat } from '../hooks/useChat';

type RouteProp = any;

export default function ChatScreen() {
  const route = useRoute<RouteProp>();
  const {
    session,
    messages,
    streaming,
    streamingContent,
    sources,
    loading,
    error,
    initSession,
    sendMessage,
    loadHistory,
  } = useChat();

  const [input, setInput] = useState('');
  const flatListRef = useRef<FlatList>(null);

  // Init session on mount
  useEffect(() => {
    const init = async () => {
      if (!session) {
        await initSession();
      } else {
        await loadHistory();
      }
    };
    init();
  }, []);

  // Handle initial message from navigation
  useEffect(() => {
    const initialMessage = route.params?.initialMessage;
    if (initialMessage && session) {
      sendMessage(initialMessage);
    }
  }, [route.params?.initialMessage, session]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (flatListRef.current && messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages, streamingContent]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || loading || streaming) return;
    sendMessage(trimmed);
    setInput('');
  };

  const handleNewChat = async () => {
    await initSession();
  };

  const renderItem = ({ item }: { item: typeof messages[0] }) => (
    <ChatBubble message={item} />
  );

  const allMessages = [...messages];
  // Add streaming message if applicable
  if (streaming && streamingContent) {
    allMessages.push({
      id: 'streaming',
      role: 'assistant',
      content: streamingContent,
      sources: null,
      created_at: new Date().toISOString(),
    });
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.headerAvatar}>
            <Ionicons name="hardware-chip-outline" size={18} color={colors.primary[600]} />
          </View>
          <View>
            <Text style={styles.headerTitle}>Chatbot RAG</Text>
            <Text style={styles.headerSubtitle}>
              {session ? 'Sessione attiva' : 'Connessione...'}
            </Text>
          </View>
        </View>
        <TouchableOpacity onPress={handleNewChat} style={styles.newChatButton}>
          <Ionicons name="add-circle-outline" size={22} color={colors.primary[600]} />
        </TouchableOpacity>
      </View>

      {/* Error */}
      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={16} color={colors.error} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={allMessages}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <View style={styles.emptyIcon}>
              <Ionicons name="chatbubble-ellipses-outline" size={48} color={colors.primary[300]} />
            </View>
            <Text style={styles.emptyTitle}>Benvenuto nel Chatbot EdilEngine</Text>
            <Text style={styles.emptySubtext}>
              Puoi chiedermi qualsiasi cosa sulle leggi italiane dell&apos;edilizia.
              Cercherò di aiutarti con risposte basate sulle fonti normative.
            </Text>
          </View>
        }
      />

      {/* Sources */}
      {sources && !streaming && Object.keys(sources).length > 0 && (
        <View style={styles.sourcesContainer}>
          <Text style={styles.sourcesTitle}>Fonti consultate:</Text>
          <Text style={styles.sourcesText} numberOfLines={2}>
            {JSON.stringify(sources, null, 0).substring(0, 200)}
          </Text>
        </View>
      )}

      {/* Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Scrivi un messaggio..."
          placeholderTextColor={colors.slate[400]}
          multiline
          maxLength={2000}
          editable={!loading && !streaming}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          blurOnSubmit={true}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!input.trim() || loading || streaming) && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!input.trim() || loading || streaming}
        >
          {loading && !streamingContent ? (
            <ActivityIndicator color={colors.white} size="small" />
          ) : (
            <Ionicons name="send" size={18} color={colors.white} />
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.slate[50],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.slate[200],
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 2,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  headerAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary[100],
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.slate[900],
  },
  headerSubtitle: {
    fontSize: 12,
    color: colors.slate[500],
  },
  newChatButton: {
    padding: 8,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginHorizontal: 12,
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
  listContent: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexGrow: 1,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingTop: 60,
  },
  emptyIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.slate[700],
    textAlign: 'center',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.slate[500],
    textAlign: 'center',
    lineHeight: 20,
  },
  sourcesContainer: {
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 12,
    backgroundColor: colors.primary[50],
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.primary[100],
  },
  sourcesTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.primary[700],
    marginBottom: 4,
  },
  sourcesText: {
    fontSize: 12,
    color: colors.slate[600],
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.slate[200],
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: colors.slate[50],
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 100,
    color: colors.slate[900],
    borderWidth: 1,
    borderColor: colors.slate[200],
  },
  sendButton: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: colors.primary[600],
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: colors.slate[300],
  },
});
