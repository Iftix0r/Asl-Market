/**
 * AslFood — Asosiy navigatsiya tuzilmasi
 *
 * Ikkita asosiy rejim:
 *  1. Oshpaz / Admin panel  → KitchenTab (Kitchen, Menu, Stats)
 *  2. Mijoz panel           → CustomerTab (Menu, Cart, Track)
 *
 * Mode tanlash ekrani birinchi ochiladi (HomeScreen).
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import { Colors } from '../utils/colors';

// Screens
import HomeScreen         from '../screens/HomeScreen';
import KitchenScreen      from '../screens/KitchenScreen';
import MenuScreen         from '../screens/MenuScreen';
import StatsScreen        from '../screens/StatsScreen';
import CustomerMenuScreen from '../screens/CustomerMenuScreen';
import OrderTrackingScreen from '../screens/OrderTrackingScreen';
import AddMenuItemScreen  from '../screens/AddMenuItemScreen';

const Stack = createNativeStackNavigator();
const Tab   = createBottomTabNavigator();

// ─── Tab ikonchasi ────────────────────────────────────────────────────────────

function TabIcon({ emoji, label, focused }) {
  return (
    <View style={styles.tabIconWrap}>
      <Text style={[styles.tabEmoji, focused && styles.tabEmojiFocused]}>
        {emoji}
      </Text>
      <Text style={[styles.tabLabel, focused && styles.tabLabelFocused]}>
        {label}
      </Text>
    </View>
  );
}

// ─── Oshpaz (Admin) Tab Navigator ────────────────────────────────────────────

function KitchenTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: Colors.amberLight,
        tabBarInactiveTintColor: Colors.textDim,
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen
        name="Kitchen"
        component={KitchenScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="🍳" label="Buyurtmalar" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Menu"
        component={MenuScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="🍔" label="Menyu" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Stats"
        component={StatsScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="📊" label="Statistika" focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// ─── Mijoz Tab Navigator ──────────────────────────────────────────────────────

function CustomerTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: Colors.primaryLight,
        tabBarInactiveTintColor: Colors.textDim,
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen
        name="CustomerMenu"
        component={CustomerMenuScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="🛍️" label="Menyu" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="TrackOrder"
        component={OrderTrackingScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="📍" label="Kuzatish" focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// ─── Asosiy Stack Navigator ───────────────────────────────────────────────────

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: Colors.bgDark },
          animation: 'slide_from_right',
        }}
      >
        {/* Mode tanlash ekrani */}
        <Stack.Screen name="Home" component={HomeScreen} />

        {/* Oshpaz paneli */}
        <Stack.Screen name="KitchenPanel" component={KitchenTabs} />

        {/* Mijoz paneli */}
        <Stack.Screen name="CustomerPanel" component={CustomerTabs} />

        {/* Taom qo'shish (MenuScreen ichidan chaqiriladi) */}
        <Stack.Screen
          name="AddMenuItem"
          component={AddMenuItemScreen}
          options={{ animation: 'slide_from_bottom' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: Colors.bgCard,
    borderTopColor: Colors.borderLight,
    borderTopWidth: 1,
    height: 65,
    paddingBottom: 8,
    paddingTop: 6,
  },
  tabIconWrap: {
    alignItems: 'center',
    justifyContent: 'center',
    gap: 2,
  },
  tabEmoji: {
    fontSize: 22,
    opacity: 0.5,
  },
  tabEmojiFocused: {
    opacity: 1,
  },
  tabLabel: {
    fontSize: 10,
    color: Colors.textDim,
    fontWeight: '500',
  },
  tabLabelFocused: {
    color: Colors.amberLight,
    fontWeight: '700',
  },
});
