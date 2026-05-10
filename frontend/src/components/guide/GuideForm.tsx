"use client";

import { useState } from "react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { Compass, Loader2 } from "lucide-react";
import type { GuideRequest } from "@/lib/types";

interface GuideFormProps {
  onSubmit: (data: GuideRequest) => void;
  loading: boolean;
}

const TIPO_INTERVENTO_OPTIONS = [
  "Nuova costruzione",
  "Ristrutturazione edilizia",
  "Restauro e risanamento conservativo",
  "Manutenzione straordinaria",
  "Manutenzione ordinaria",
  "Ampliamento",
  "Sopraelevazione",
  "Demolizione e ricostruzione",
  "Cambio destinazione d'uso",
];

const MATERIALE_OPTIONS = [
  "Calcestruzzo armato",
  "Acciaio",
  "Legno",
  "Muratura portante",
  "Prefabbricato",
  "Misto",
];

const DESTINAZIONE_OPTIONS = [
  "Residenziale",
  "Commerciale",
  "Industriale/Artigianale",
  "Agricolo",
  "Turistico/Ricettivo",
  "Uffici",
  "Servizi pubblici",
  "Residenziale + Commerciale",
];

export default function GuideForm({ onSubmit, loading }: GuideFormProps) {
  const [form, setForm] = useState<GuideRequest>({
    regione: "",
    provincia: "",
    comune: "",
    tipo_intervento: "",
    materiale_costruzione: "",
    destinazione_uso: "",
    num_unita: 1,
    superficie_terreno_mq: null,
    volume_previsto_mc: null,
  });

  const handleChange = (
    field: keyof GuideRequest,
    value: string | number | null
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  const isValid =
    form.regione.trim() &&
    form.provincia.trim() &&
    form.comune.trim() &&
    form.tipo_intervento &&
    form.destinazione_uso;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Location */}
      <div>
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          Dove si trova l&apos;intervento?
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input
            label="Regione"
            placeholder="es. Lombardia"
            value={form.regione}
            onChange={(e) => handleChange("regione", e.target.value)}
            required
          />
          <Input
            label="Provincia"
            placeholder="es. Milano"
            value={form.provincia}
            onChange={(e) => handleChange("provincia", e.target.value)}
            required
          />
          <Input
            label="Comune"
            placeholder="es. Milano"
            value={form.comune}
            onChange={(e) => handleChange("comune", e.target.value)}
            required
          />
        </div>
      </div>

      {/* Intervento */}
      <div>
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          Cosa vuoi realizzare?
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Tipo di intervento *
            </label>
            <select
              value={form.tipo_intervento}
              onChange={(e) =>
                handleChange("tipo_intervento", e.target.value)
              }
              required
              className="block w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                transition-colors duration-200"
            >
              <option value="">Seleziona tipo intervento</option>
              {TIPO_INTERVENTO_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Destinazione d&apos;uso *
            </label>
            <select
              value={form.destinazione_uso}
              onChange={(e) =>
                handleChange("destinazione_uso", e.target.value)
              }
              required
              className="block w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                transition-colors duration-200"
            >
              <option value="">Seleziona destinazione</option>
              {DESTINAZIONE_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Dettagli tecnici */}
      <div>
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          Dettagli tecnici
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Materiale di costruzione
            </label>
            <select
              value={form.materiale_costruzione || ""}
              onChange={(e) =>
                handleChange(
                  "materiale_costruzione",
                  e.target.value || null
                )
              }
              className="block w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                transition-colors duration-200"
            >
              <option value="">Non specificato</option>
              {MATERIALE_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Numero unità"
            type="number"
            min={1}
            value={String(form.num_unita)}
            onChange={(e) =>
              handleChange("num_unita", parseInt(e.target.value) || 1)
            }
          />

          <Input
            label="Superficie terreno (mq)"
            type="number"
            min={0}
            step={0.01}
            placeholder="es. 500"
            value={
              form.superficie_terreno_mq !== null
                ? String(form.superficie_terreno_mq)
                : ""
            }
            onChange={(e) =>
              handleChange(
                "superficie_terreno_mq",
                e.target.value ? parseFloat(e.target.value) : null
              )
            }
          />

          <Input
            label="Volume previsto (mc)"
            type="number"
            min={0}
            step={0.01}
            placeholder="es. 1500"
            value={
              form.volume_previsto_mc !== null
                ? String(form.volume_previsto_mc)
                : ""
            }
            onChange={(e) =>
              handleChange(
                "volume_previsto_mc",
                e.target.value ? parseFloat(e.target.value) : null
              )
            }
          />
        </div>
      </div>

      {/* Submit */}
      <div className="flex justify-end">
        <Button
          type="submit"
          size="lg"
          disabled={!isValid || loading}
          leftIcon={
            loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Compass className="w-5 h-5" />
            )
          }
        >
          {loading ? "Generazione in corso..." : "Genera guida personalizzata"}
        </Button>
      </div>
    </form>
  );
}
