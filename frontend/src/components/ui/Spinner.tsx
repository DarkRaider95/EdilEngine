import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const sizeStyles: Record<"sm" | "md" | "lg", string> = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-3",
  lg: "h-12 w-12 border-4",
};

export default function Spinner({
  size = "md",
  className,
  label = "Caricamento...",
}: SpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <div
        className={cn(
          "animate-spin rounded-full border-slate-200 border-t-primary-600",
          sizeStyles[size]
        )}
        role="status"
        aria-label={label}
      />
      {label && <p className="text-sm text-slate-500">{label}</p>}
    </div>
  );
}
