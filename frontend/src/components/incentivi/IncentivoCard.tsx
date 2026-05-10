import Link from "next/link";
import { Calendar, Building2, Percent } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { formatDate, truncateText, formatAliquota } from "@/lib/utils";
import type { IncentivoBase } from "@/lib/types";

interface IncentivoCardProps {
  incentivo: IncentivoBase;
}

export default function IncentivoCard({ incentivo }: IncentivoCardProps) {
  const href = incentivo.id
    ? `/incentivi/${incentivo.id}`
    : `/incentivi/${encodeURIComponent(incentivo.titolo)}`;

  return (
    <Link href={href}>
      <Card hover className="h-full">
        <div className="flex flex-col gap-3">
          {/* Tipo + Aliquota */}
          <div className="flex items-center justify-between gap-2">
            {incentivo.tipo && (
              <Badge variant="success" size="sm">
                {incentivo.tipo}
              </Badge>
            )}
            {incentivo.aliquota !== null && incentivo.aliquota !== undefined && (
              <span className="flex items-center gap-1 text-sm font-bold text-green-700">
                <Percent className="w-4 h-4" />
                {formatAliquota(incentivo.aliquota)}
              </span>
            )}
          </div>

          {/* Titolo */}
          <h3 className="text-base font-semibold text-slate-900 line-clamp-2 leading-snug">
            {incentivo.titolo}
          </h3>

          {/* Descrizione */}
          {incentivo.descrizione && (
            <p className="text-sm text-slate-600 line-clamp-3">
              {truncateText(incentivo.descrizione, 150)}
            </p>
          )}

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-auto pt-2">
            {incentivo.ente_erogatore && (
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5" />
                {truncateText(incentivo.ente_erogatore, 30)}
              </span>
            )}
            {incentivo.scadenza && (
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                Scade {formatDate(incentivo.scadenza)}
              </span>
            )}
          </div>
        </div>
      </Card>
    </Link>
  );
}
