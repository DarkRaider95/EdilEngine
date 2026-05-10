"use client";

import { useState } from "react";
import GuideForm from "@/components/guide/GuideForm";
import GuideResult from "@/components/guide/GuideResult";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import { useGuide } from "@/hooks/useGuide";
import { Compass, ArrowLeft } from "lucide-react";
import type { GuideRequest } from "@/lib/types";

export default function GuidaPersonalizzataPage() {
  const { result, loading, error, submitGuide, clearResult } = useGuide();

  const handleSubmit = (data: GuideRequest) => {
    submitGuide(data);
  };

  return (
    <div className="container-page py-8">
      <div className="max-w-4xl mx-auto">
        {!result && (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-3 flex items-center gap-3">
                <Compass className="w-8 h-8 text-primary-600" />
                Guida Personalizzata
              </h1>
              <p className="text-slate-600">
                Compila il form con i dettagli del tuo intervento edilizio. Il
                sistema analizzerà vincoli territoriali, permessi necessari e
                incentivi applicabili per generare una guida passo-passo.
              </p>
            </div>

            {error && (
              <Card className="mb-6 border-red-300 bg-red-50">
                <p className="text-red-700">{error}</p>
              </Card>
            )}

            <Card>
              <GuideForm onSubmit={handleSubmit} loading={loading} />
            </Card>
          </>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <Spinner size="lg" label="Generazione guida in corso..." />
            <p className="text-sm text-slate-500 mt-4 max-w-md text-center">
              Stiamo analizzando i vincoli territoriali, i permessi necessari e
              gli incentivi disponibili per il tuo progetto. Potrebbe volerci
              qualche secondo.
            </p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div>
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-slate-900">
                La tua guida personalizzata
              </h1>
              <Button
                variant="outline"
                size="sm"
                onClick={clearResult}
                leftIcon={<ArrowLeft size={16} />}
              >
                Nuova guida
              </Button>
            </div>

            <GuideResult guide={result} />
          </div>
        )}
      </div>
    </div>
  );
}
