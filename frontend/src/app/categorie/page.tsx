"use client";

import { useState, useEffect } from "react";
import { getCategorie } from "@/lib/api";
import type { CategoriaTree } from "@/lib/types";
import Card from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import { ChevronRight, ChevronDown, FolderTree } from "lucide-react";

function CategoryNode({
  category,
  level = 0,
}: {
  category: CategoriaTree;
  level?: number;
}) {
  const [isExpanded, setIsExpanded] = useState(level < 1);
  const hasChildren = category.children && category.children.length > 0;

  return (
    <div className="animate-fade-in">
      <button
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
        className={`flex items-center gap-2 w-full text-left py-2.5 px-3 rounded-lg transition-colors
          ${hasChildren ? "hover:bg-slate-100 cursor-pointer" : "cursor-default"}
          ${level === 0 ? "text-base font-semibold text-slate-900" : "text-sm text-slate-700"}`}
        style={{ paddingLeft: `${12 + level * 20}px` }}
      >
        {hasChildren ? (
          isExpanded ? (
            <ChevronDown className="w-4 h-4 text-primary-500 flex-shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-primary-500 flex-shrink-0" />
          )
        ) : (
          <span className="w-4 h-4 flex-shrink-0" />
        )}
        <span>{category.nome}</span>
        {hasChildren && (
          <span className="text-xs text-slate-400 ml-2">
            ({category.children.length})
          </span>
        )}
      </button>

      {isExpanded && hasChildren && (
        <div>
          {category.children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CategoriePage() {
  const [categorie, setCategorie] = useState<CategoriaTree[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategorie();
  }, []);

  async function loadCategorie() {
    setLoading(true);
    setError(null);
    try {
      const data = await getCategorie();
      setCategorie(data);
    } catch (err) {
      setError(
        "Errore nel caricamento delle categorie. Verifica che il backend sia attivo."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-page py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <FolderTree className="w-8 h-8 text-primary-600" />
            Categorie normative
          </h1>
          <p className="mt-3 text-slate-600">
            Esplora la normativa edilizia organizzata per categorie tematiche.
            Ogni categoria raggruppa leggi e regolamenti correlati.
          </p>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <Spinner size="lg" label="Caricamento categorie..." />
          </div>
        )}

        {error && (
          <Card>
            <p className="text-red-600">{error}</p>
          </Card>
        )}

        {!loading && !error && categorie.length === 0 && (
          <Card>
            <p className="text-slate-500 text-center py-8">
              Nessuna categoria disponibile. Popola il database per visualizzare
              le categorie.
            </p>
          </Card>
        )}

        {!loading && !error && categorie.length > 0 && (
          <Card>
            <div className="divide-y divide-slate-100">
              {categorie.map((cat) => (
                <CategoryNode key={cat.id} category={cat} />
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
