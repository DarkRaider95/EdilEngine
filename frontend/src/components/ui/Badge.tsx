import { cn } from "@/lib/utils";

type BadgeVariant =
  | "default"
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "info";

interface BadgeProps {
  variant?: BadgeVariant;
  size?: "sm" | "md";
  className?: string;
  children: React.ReactNode;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-slate-100 text-slate-700",
  primary: "bg-primary-100 text-primary-700",
  success: "bg-green-100 text-green-700",
  warning: "bg-amber-100 text-amber-700",
  danger: "bg-red-100 text-red-700",
  info: "bg-blue-100 text-blue-700",
};

const sizeStyles: Record<"sm" | "md", string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm",
};

/**
 * Mappa il tipo di legge a una variante badge.
 */
export function leggeTipoToVariant(tipo: string | null): BadgeVariant {
  if (!tipo) return "default";
  const t = tipo.toLowerCase();
  if (t.includes("legge") || t.includes("l.")) return "primary";
  if (t.includes("decreto") || t.includes("d.l.") || t.includes("d.p.r."))
    return "info";
  if (t.includes("regolamento") || t.includes("direttiva")) return "warning";
  if (t.includes("circolare") || t.includes("linee guida")) return "success";
  return "default";
}

export default function Badge({
  variant = "default",
  size = "sm",
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
