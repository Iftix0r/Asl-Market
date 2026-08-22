/**
 * AddMenuItemScreen — Yangi taom qo'shish formasi
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  SafeAreaView, StatusBar, ScrollView, Alert,
  ActivityIndicator, KeyboardAvoidingView, Platform,
} from 'react-native';

import { addFoodItem, getCategories } from '../services/api';
import { Colors } from '../utils/colors';

export default function AddMenuItemScreen({ navigation }) {
  const [categories, setCategories] = useState([]);
  const [saving,     setSaving]     = useState(false);

  const [name,       setName]       = useState('');
  const [price,      setPrice]      = useState('');
  const [prepTime,   setPrepTime]   = useState('15');
  const [imageUrl,   setImageUrl]   = useState('');
  const [ingredients, setIngredients] = useState('');
  const [categoryId, setCategoryId] = useState(null);

  useEffect(() => {
    getCategories().then(res => {
      if (res.success) {
        setCategories(res.categories);
        if (res.categories.length > 0) setCategoryId(res.categories[0].id);
      }
    });
  }, []);

  const handleSave = async () => {
    if (!name.trim())    { Alert.alert('Xatolik', 'Taom nomini kiriting'); return; }
    if (!price.trim())   { Alert.alert('Xatolik', 'Narxni kiriting'); return; }
    if (!categoryId)     { Alert.alert('Xatolik', 'Kategoriya tanlang'); return; }

    setSaving(true);
    const res = await addFoodItem({
      name: name.trim(),
      price: parseFloat(price),
      preparation_time_mins: parseInt(prepTime) || 15,
      image_url: imageUrl.trim(),
      ingredients: ingredients.trim(),
      category_id: categoryId,
    });

    setSaving(false);

    if (res.success) {
      Alert.alert('Muvaffaqiyat', `"${res.item.name}" menyuga qo'shildi!`, [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } else {
      Alert.alert('Xatolik', res.error || 'Saqlashda xatolik yuz berdi');
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bgDark} />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backBtnText}>← Orqaga</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Yangi Taom</Text>
          <View style={{ width: 70 }} />
        </View>

        <ScrollView contentContainerStyle={styles.form} keyboardShouldPersistTaps="handled">

          {/* Nom */}
          <Field label="Taom nomi *">
            <TextInput
              style={styles.input}
              placeholder="Masalan: Beef Lavash Big"
              placeholderTextColor={Colors.textDim}
              value={name}
              onChangeText={setName}
            />
          </Field>

          {/* Narx */}
          <Field label="Narx (so'm) *">
            <TextInput
              style={styles.input}
              placeholder="Masalan: 35000"
              placeholderTextColor={Colors.textDim}
              value={price}
              onChangeText={setPrice}
              keyboardType="numeric"
            />
          </Field>

          {/* Kategoriya */}
          <Field label="Kategoriya *">
            <View style={styles.catRow}>
              {categories.map(cat => (
                <TouchableOpacity
                  key={cat.id}
                  style={[
                    styles.catChip,
                    categoryId === cat.id && styles.catChipActive,
                  ]}
                  onPress={() => setCategoryId(cat.id)}
                >
                  <Text style={[
                    styles.catChipText,
                    categoryId === cat.id && styles.catChipTextActive,
                  ]}>
                    {cat.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </Field>

          {/* Tayyorlanish vaqti */}
          <Field label="Tayyorlanish vaqti (daqiqa)">
            <TextInput
              style={styles.input}
              placeholder="15"
              placeholderTextColor={Colors.textDim}
              value={prepTime}
              onChangeText={setPrepTime}
              keyboardType="numeric"
            />
          </Field>

          {/* Rasm URL */}
          <Field label="Rasm URL (ixtiyoriy)">
            <TextInput
              style={styles.input}
              placeholder="https://images.unsplash.com/..."
              placeholderTextColor={Colors.textDim}
              value={imageUrl}
              onChangeText={setImageUrl}
              autoCapitalize="none"
            />
          </Field>

          {/* Tarkib */}
          <Field label="Tarkibi / Retsept (ixtiyoriy)">
            <TextInput
              style={[styles.input, styles.textarea]}
              placeholder="Mol go'shti, pishloq, pomidor..."
              placeholderTextColor={Colors.textDim}
              value={ingredients}
              onChangeText={setIngredients}
              multiline
              numberOfLines={3}
            />
          </Field>

          {/* Saqlash tugmasi */}
          <TouchableOpacity
            style={[styles.saveBtn, saving && { opacity: 0.7 }]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator color={Colors.bgDark} />
            ) : (
              <Text style={styles.saveBtnText}>✅ Menyuga qo'shish</Text>
            )}
          </TouchableOpacity>

        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── Field wrapper ─────────────────────────────────────────────────────────────

function Field({ label, children }) {
  return (
    <View style={styles.fieldWrap}>
      <Text style={styles.label}>{label}</Text>
      {children}
    </View>
  );
}

// ─── Uslublar ─────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bgDark },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  backBtn: { padding: 4 },
  backBtnText: { color: Colors.primaryLight, fontSize: 14, fontWeight: '600' },
  headerTitle: { fontSize: 16, fontWeight: '800', color: Colors.textMain },

  form: { padding: 16, gap: 16, paddingBottom: 40 },

  fieldWrap: { gap: 6 },
  label: { fontSize: 13, fontWeight: '600', color: Colors.textMuted },
  input: {
    backgroundColor: Colors.bgCard,
    borderWidth: 1,
    borderColor: Colors.borderSubtle,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: Colors.textMain,
    fontSize: 14,
  },
  textarea: { height: 80, textAlignVertical: 'top' },

  catRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  catChip: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 8,
    backgroundColor: Colors.bgCard,
    borderWidth: 1,
    borderColor: Colors.borderSubtle,
  },
  catChipActive: {
    backgroundColor: Colors.amberAlpha15,
    borderColor: Colors.amberAlpha30,
  },
  catChipText: { fontSize: 12, color: Colors.textMuted, fontWeight: '600' },
  catChipTextActive: { color: Colors.amberLight },

  saveBtn: {
    backgroundColor: Colors.amber,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 8,
  },
  saveBtnText: { fontSize: 15, fontWeight: '800', color: Colors.bgDark },
});
