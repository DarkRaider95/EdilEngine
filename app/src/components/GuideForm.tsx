// ============================================================
// EdilEngine - GuideForm Component
// ============================================================

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import type { GuideRequest } from '../services/types';

interface GuideFormProps {
  onSubmit: (data: GuideRequest) => void;
  loading: boolean;
}

const TIPO_INTERVENTO_OPTIONS = [
  'Nuova costruzione',
  'Ristrutturazione edilizia',
  'Restauro e risanamento conservativo',
  'Manutenzione straordinaria',
  'Manutenzione ordinaria',
  'Ampliamento',
  'Sopraelevazione',
  'Demolizione e ricostruzione',
  "Cambio destinazione d'uso",
];

const MATERIALE_OPTIONS = [
  'Calcestruzzo armato',
  'Acciaio',
  'Legno',
  'Muratura portante',
  'Prefabbricato',
  'Misto',
];

const DESTINAZIONE_OPTIONS = [
  'Residenziale',
  'Commerciale',
  'Industriale/Artigianale',
  'Agricolo',
  'Turistico/Ricettivo',
  'Uffici',
  'Servizi pubblici',
  'Residenziale + Commerciale',
];

interface PickerFieldProps {
  label: string;
  value: string;
  options: string[];
  onValueChange: (value: string) => void;
  required?: boolean;
  placeholder?: string;
}

function PickerField({ label, value, options, onValueChange, required, placeholder }: PickerFieldProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={fieldStyles.container}>
      <Text style={fieldStyles.label}>
        {label} {required && <Text style={fieldStyles.required}>*</Text>}
      </Text>
      <TouchableOpacity
        style={fieldStyles.pickerButton}
        onPress={() => setExpanded(!expanded)}
      >
        <Text style={[fieldStyles.pickerText, !value && fieldStyles.placeholderText]}>
          {value || placeholder || 'Seleziona...'}
        </Text>
        <Ionicons
          name={expanded ? 'chevron-up' : 'chevron-down'}
          size={20}
          color={colors.slate[400]}
        />
      </TouchableOpacity>
      {expanded && (
        <View style={fieldStyles.optionsContainer}>
          <ScrollView style={fieldStyles.optionsScroll} nestedScrollEnabled>
            {options.map((opt) => (
              <TouchableOpacity
                key={opt}
                style={[fieldStyles.option, value === opt && fieldStyles.optionSelected]}
                onPress={() => {
                  onValueChange(opt);
                  setExpanded(false);
                }}
              >
                <Text style={[fieldStyles.optionText, value === opt && fieldStyles.optionTextSelected]}>
                  {opt}
                </Text>
                {value === opt && (
                  <Ionicons name="checkmark" size={18} color={colors.primary[600]} />
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const fieldStyles = StyleSheet.create({
  container: {
    marginBottom: 12,
    position: 'relative',
    zIndex: 1,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.slate[700],
    marginBottom: 6,
  },
  required: {
    color: colors.error,
  },
  pickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: colors.slate[300],
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    backgroundColor: colors.white,
  },
  pickerText: {
    fontSize: 16,
    color: colors.slate[900],
  },
  placeholderText: {
    color: colors.slate[400],
  },
  optionsContainer: {
    position: 'absolute',
    top: '100%',
    left: 0,
    right: 0,
    zIndex: 10,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.slate[200],
    borderRadius: 12,
    marginTop: 4,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    maxHeight: 200,
  },
  optionsScroll: {
    maxHeight: 195,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.slate[100],
  },
  optionSelected: {
    backgroundColor: colors.primary[50],
  },
  optionText: {
    fontSize: 15,
    color: colors.slate[700],
  },
  optionTextSelected: {
    color: colors.primary[700],
    fontWeight: '600',
  },
});

export default function GuideForm({ onSubmit, loading }: GuideFormProps) {
  const [form, setForm] = useState<GuideRequest>({
    regione: '',
    provincia: '',
    comune: '',
    tipo_intervento: '',
    materiale_costruzione: null,
    destinazione_uso: '',
    num_unita: 1,
    superficie_terreno_mq: null,
    volume_previsto_mc: null,
  });

  const handleChange = (field: keyof GuideRequest, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(form);
  };

  const isValid =
    form.regione.trim() &&
    form.provincia.trim() &&
    form.comune.trim() &&
    form.tipo_intervento &&
    form.destinazione_uso;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Location */}
      <Text style={styles.sectionTitle}>Dove si trova l&apos;intervento?</Text>
      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Regione *</Text>
          <TextInput
            style={styles.input}
            placeholder="es. Lombardia"
            placeholderTextColor={colors.slate[400]}
            value={form.regione}
            onChangeText={(v) => handleChange('regione', v)}
          />
        </View>
      </View>
      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Provincia *</Text>
          <TextInput
            style={styles.input}
            placeholder="es. Milano"
            placeholderTextColor={colors.slate[400]}
            value={form.provincia}
            onChangeText={(v) => handleChange('provincia', v)}
          />
        </View>
        <View style={styles.spacer} />
        <View style={styles.flex1}>
          <Text style={styles.label}>Comune *</Text>
          <TextInput
            style={styles.input}
            placeholder="es. Milano"
            placeholderTextColor={colors.slate[400]}
            value={form.comune}
            onChangeText={(v) => handleChange('comune', v)}
          />
        </View>
      </View>

      {/* Intervento */}
      <Text style={styles.sectionTitle}>Cosa vuoi realizzare?</Text>
      <PickerField
        label="Tipo di intervento"
        value={form.tipo_intervento}
        options={TIPO_INTERVENTO_OPTIONS}
        onValueChange={(v) => handleChange('tipo_intervento', v)}
        required
        placeholder="Seleziona tipo intervento"
      />
      <PickerField
        label="Destinazione d'uso"
        value={form.destinazione_uso}
        options={DESTINAZIONE_OPTIONS}
        onValueChange={(v) => handleChange('destinazione_uso', v)}
        required
        placeholder="Seleziona destinazione"
      />

      {/* Dettagli tecnici */}
      <Text style={styles.sectionTitle}>Dettagli tecnici</Text>
      <PickerField
        label="Materiale di costruzione"
        value={form.materiale_costruzione || ''}
        options={MATERIALE_OPTIONS}
        onValueChange={(v) => handleChange('materiale_costruzione', v || null)}
        placeholder="Non specificato"
      />

      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Numero unità</Text>
          <TextInput
            style={styles.input}
            keyboardType="numeric"
            value={String(form.num_unita)}
            onChangeText={(v) => handleChange('num_unita', parseInt(v) || 1)}
          />
        </View>
        <View style={styles.spacer} />
        <View style={styles.flex1}>
          <Text style={styles.label}>Superficie (mq)</Text>
          <TextInput
            style={styles.input}
            keyboardType="numeric"
            placeholder="es. 500"
            placeholderTextColor={colors.slate[400]}
            value={form.superficie_terreno_mq !== null ? String(form.superficie_terreno_mq) : ''}
            onChangeText={(v) =>
              handleChange('superficie_terreno_mq', v ? parseFloat(v) : null)
            }
          />
        </View>
      </View>

      <View style={styles.row}>
        <View style={styles.halfWidth}>
          <Text style={styles.label}>Volume previsto (mc)</Text>
          <TextInput
            style={styles.input}
            keyboardType="numeric"
            placeholder="es. 1500"
            placeholderTextColor={colors.slate[400]}
            value={form.volume_previsto_mc !== null ? String(form.volume_previsto_mc) : ''}
            onChangeText={(v) =>
              handleChange('volume_previsto_mc', v ? parseFloat(v) : null)
            }
          />
        </View>
      </View>

      {/* Submit */}
      <TouchableOpacity
        style={[styles.submitButton, (!isValid || loading) && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={!isValid || loading}
      >
        {loading ? (
          <ActivityIndicator color={colors.white} size="small" />
        ) : (
          <Ionicons name="compass-outline" size={20} color={colors.white} />
        )}
        <Text style={styles.submitText}>
          {loading ? 'Generazione in corso...' : 'Genera guida personalizzata'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.slate[800],
    marginTop: 20,
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  flex1: {
    flex: 1,
  },
  halfWidth: {
    width: '50%',
  },
  spacer: {
    width: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.slate[700],
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.slate[300],
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.slate[900],
    backgroundColor: colors.white,
    marginBottom: 12,
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    backgroundColor: colors.primary[600],
    borderRadius: 14,
    paddingVertical: 16,
    marginTop: 24,
    shadowColor: colors.primary[600],
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  submitButtonDisabled: {
    backgroundColor: colors.slate[300],
    shadowOpacity: 0,
    elevation: 0,
  },
  submitText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
});
