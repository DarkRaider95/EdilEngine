// ============================================================
// EdilEngine - ChatBubble Component
// ============================================================

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import type { ChatMessageResponse } from '../services/types';

interface ChatBubbleProps {
  message: ChatMessageResponse;
  isStreaming?: boolean;
}

export default function ChatBubble({ message, isStreaming = false }: ChatBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <View style={[styles.container, isUser ? styles.userContainer : styles.assistantContainer]}>
      {/* Avatar for assistant */}
      {!isUser && (
        <View style={styles.avatarAssistant}>
          <Ionicons name="hardware-chip-outline" size={16} color={colors.primary[600]} />
        </View>
      )}

      {/* Bubble */}
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        <Text style={[styles.text, isUser ? styles.userText : styles.assistantText]}>
          {message.content || ''}
          {isStreaming && (
            <Text style={styles.cursor}> ▌</Text>
          )}
        </Text>
        {!isStreaming && message.created_at && (
          <Text style={[styles.time, isUser ? styles.userTime : styles.assistantTime]}>
            {new Date(message.created_at).toLocaleTimeString('it-IT', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        )}
      </View>

      {/* Avatar for user */}
      {isUser && (
        <View style={styles.avatarUser}>
          <Ionicons name="person" size={16} color={colors.green[600]} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
    gap: 8,
  },
  userContainer: {
    justifyContent: 'flex-end',
  },
  assistantContainer: {
    justifyContent: 'flex-start',
  },
  avatarAssistant: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary[100],
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarUser: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.green[100],
    alignItems: 'center',
    justifyContent: 'center',
  },
  bubble: {
    maxWidth: '75%',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 18,
  },
  userBubble: {
    backgroundColor: colors.primary[600],
    borderBottomRightRadius: 6,
  },
  assistantBubble: {
    backgroundColor: colors.slate[100],
    borderBottomLeftRadius: 6,
  },
  text: {
    fontSize: 15,
    lineHeight: 22,
  },
  userText: {
    color: colors.white,
  },
  assistantText: {
    color: colors.slate[900],
  },
  cursor: {
    color: colors.slate[500],
  },
  time: {
    fontSize: 11,
    marginTop: 6,
  },
  userTime: {
    color: colors.primary[200],
  },
  assistantTime: {
    color: colors.slate[400],
  },
});
