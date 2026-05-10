import Link from "next/link";
import { FileText, Calendar, Building2 } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge, { leggeTipoToVariant } from "@/components/ui/Badge";
import { formatDate, truncateText } from "@/lib/utils";
import type { LeggeBase } from "@/lib/types";

interface LeggeCardProps {
  legge: LeggeBase;
}

export default function LeggeCard({ legge }: LeggeCardProps) {
  const href = legge.id
    ? `/leggi/${legge.id}`
    : `/leggi/${encodeURIComponent(legge.titolo)}`;

  return (
    <Link href={href}>
      <Card hover className="h-full">
        <div className="flex flex-col gap-3">
          {/* Tipo badge */}
          {legge.tipo && (
            <Badge variant={leggeTipoToVariant(legge.tipo)} size="sm">
              {legge.tipo}
            </Badge>
          )}

          {/* Titolo */}
          <h3 className="text-base font-semibold text-slate-900 line-clamp-2 leading-snug">
            {legge.titolo}
          </h3>

          {/* Meta info */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
            {legge.numero && (
              <span className="flex items-center gap-1">
                <FileText className="w-3.5 h-3.5" />
                n. {legge.numero}
              </span>
            )}
            {legge.data_emanazione && (
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {formatDate(legge.data_emanazione)}
              </span>
            )}
            {legge.autorita && (
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5" />
                {truncateText(legge.autorita, 40)}
              </span>
            )}
          </div>

          {/* URL Fonte */}
          {legge.url_fonte && (
            <a
              href={legge.url_fonte}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary-600 hover:text-primary-800 truncate"
              onClick={(e) => e.stopPropagation()}
            >
              {legge.url_fonte}
            </a>
          )}
        </div>
      </Card>
    </Link>
  );
}
