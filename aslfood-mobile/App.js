/**
 * AslFood Mobile — Asosiy entry point
 */

import 'react-native-gesture-handler';
import React from 'react';
import { StyleSheet } from 'react-native';

import AppNavigator from './src/navigation/AppNavigator';
import Toast       from './src/components/Toast';
import { Colors }  from './src/utils/colors';

export default function App() {
  return (
    <>
      <AppNavigator />
      <Toast />
    </>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: Colors.bgDark,
  },
});
