"use client";

import { useState } from "react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { Search, RotateCcw } from "lucide-react";

export interface IncentivoFilterValues {
  tipo: string;
  ente_erogatore: string;
  scadenza_dopo: string;
}

interface IncentivoFilterProps {
  onFilter: (values: IncentivoFilterValues) => void;
  onReset: () => void;
  loading?: boolean;
}

export default function IncentivoFilter({
  onFilter,
  onReset,
  loading,
}: IncentivoFilterProps) {
  const [values, setValues] = useState<IncentivoFilterValues>({
    tipo: "",
    ente_erogatore: "",
    scadenza_dopo: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter(values);
  };

  const handleReset = () => {
    setValues({ tipo: "", ente_erogatore: "", scadenza_dopo: "" });
    onReset();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-xl border border-slate-200 p-5 mb-6"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Input
          label="Tipo incentivo"
          placeholder="es. Superbonus, Ecobonus..."
          value={values.tipo}
          onChange={(e) => setValues({ ...values, tipo: e.target.value })}
        />
        <Input
          label="Ente erogatore"
          placeholder="es. ENEA, GSE..."
          value={values.ente_erogatore}
          onChange={(e) =>
            setValues({ ...values, ente_erogatore: e.target.value })
          }
        />
        <Input
          label="Scadenza dopo il"
          type="date"
          value={values.scadenza_dopo}
          onChange={(e) =>
            setValues({ ...values, scadenza_dopo: e.target.value })
          }
        />
        <div className="flex items-end gap-2">
          <Button type="submit" loading={loading} leftIcon={<Search size={16} />}>
            Filtra
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleReset}
            leftIcon={<RotateCcw size={16} />}
          >
            Reset
          </Button>
        </div>
      </div>
    </form>
  );
}
