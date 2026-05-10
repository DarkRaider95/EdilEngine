// ============================================================
// EdilEngine - RootNavigator
// Bottom tabs + Stack navigators
// ============================================================

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';

// Screens
import HomeScreen from '../screens/HomeScreen';
import SearchScreen from '../screens/SearchScreen';
import LeggeDetailScreen from '../screens/LeggeDetailScreen';
import IncentiviScreen from '../screens/IncentiviScreen';
import IncentivoDetailScreen from '../screens/IncentivoDetailScreen';
import ChatScreen from '../screens/ChatScreen';
import GuideScreen from '../screens/GuideScreen';
import ProfileScreen from '../screens/ProfileScreen';

// ============================================================
// Types
// ============================================================

export type RootTabParamList = {
  HomeTab: undefined;
  CercaTab: undefined;
  ChatTab: undefined;
  ProfiloTab: undefined;
};

export type HomeStackParamList = {
  Home: undefined;
  LeggeDetail: { id: string };
  IncentivoDetail: { id: string };
  Guida: undefined;
};

export type CercaStackParamList = {
  Cerca: { query?: string } | undefined;
  LeggeDetail: { id: string };
};

export type ChatStackParamList = {
  Chat: { initialMessage?: string } | undefined;
  LeggeDetail: { id: string };
};

export type ProfiloStackParamList = {
  Profilo: undefined;
};

// ============================================================
// Stack Navigator per Home
// ============================================================

const HomeStack = createNativeStackNavigator<HomeStackParamList>();

function HomeStackNavigator() {
  return (
    <HomeStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.slate[900],
        headerTitleStyle: { fontWeight: '600' },
        headerShadowVisible: false,
      }}
    >
      <HomeStack.Screen
        name="Home"
        component={HomeScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="LeggeDetail"
        component={LeggeDetailScreen}
        options={{ title: 'Dettaglio Legge' }}
      />
      <HomeStack.Screen
        name="IncentivoDetail"
        component={IncentivoDetailScreen}
        options={{ title: 'Dettaglio Incentivo' }}
      />
      <HomeStack.Screen
        name="Guida"
        component={GuideScreen}
        options={{ title: 'Guida Personalizzata' }}
      />
    </HomeStack.Navigator>
  );
}

// ============================================================
// Stack Navigator per Cerca
// ============================================================

const CercaStack = createNativeStackNavigator<CercaStackParamList>();

function CercaStackNavigator() {
  return (
    <CercaStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.slate[900],
        headerTitleStyle: { fontWeight: '600' },
        headerShadowVisible: false,
      }}
    >
      <CercaStack.Screen
        name="Cerca"
        component={SearchScreen}
        options={{ headerShown: false }}
      />
      <CercaStack.Screen
        name="LeggeDetail"
        component={LeggeDetailScreen}
        options={{ title: 'Dettaglio Legge' }}
      />
    </CercaStack.Navigator>
  );
}

// ============================================================
// Stack Navigator per Chat
// ============================================================

const ChatStack = createNativeStackNavigator<ChatStackParamList>();

function ChatStackNavigator() {
  return (
    <ChatStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.slate[900],
        headerTitleStyle: { fontWeight: '600' },
        headerShadowVisible: false,
      }}
    >
      <ChatStack.Screen
        name="Chat"
        component={ChatScreen}
        options={{ headerShown: false }}
      />
      <ChatStack.Screen
        name="LeggeDetail"
        component={LeggeDetailScreen}
        options={{ title: 'Dettaglio Legge' }}
      />
    </ChatStack.Navigator>
  );
}

// ============================================================
// Stack Navigator per Profilo
// ============================================================

const ProfiloStack = createNativeStackNavigator<ProfiloStackParamList>();

function ProfiloStackNavigator() {
  return (
    <ProfiloStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.slate[900],
        headerTitleStyle: { fontWeight: '600' },
        headerShadowVisible: false,
      }}
    >
      <ProfiloStack.Screen
        name="Profilo"
        component={ProfileScreen}
        options={{ title: 'Profilo' }}
      />
    </ProfiloStack.Navigator>
  );
}

// ============================================================
// Bottom Tab Navigator
// ============================================================

const Tab = createBottomTabNavigator<RootTabParamList>();

export default function RootNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopColor: colors.slate[200],
          borderTopWidth: 1,
          paddingTop: 6,
          paddingBottom: 8,
          height: 60,
        },
        tabBarActiveTintColor: colors.primary[600],
        tabBarInactiveTintColor: colors.slate[400],
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'help-circle';

          switch (route.name) {
            case 'HomeTab':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'CercaTab':
              iconName = focused ? 'search' : 'search-outline';
              break;
            case 'ChatTab':
              iconName = focused ? 'chatbubble-ellipses' : 'chatbubble-ellipses-outline';
              break;
            case 'ProfiloTab':
              iconName = focused ? 'person' : 'person-outline';
              break;
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeStackNavigator}
        options={{ tabBarLabel: 'Home' }}
      />
      <Tab.Screen
        name="CercaTab"
        component={CercaStackNavigator}
        options={{ tabBarLabel: 'Cerca' }}
      />
      <Tab.Screen
        name="ChatTab"
        component={ChatStackNavigator}
        options={{ tabBarLabel: 'Chat' }}
      />
      <Tab.Screen
        name="ProfiloTab"
        component={ProfiloStackNavigator}
        options={{ tabBarLabel: 'Profilo' }}
      />
    </Tab.Navigator>
  );
}
