import { cn } from "@/lib/utils";

interface CardProps {
  title?: string;
  subtitle?: string;
  className?: string;
  bodyClassName?: string;
  footer?: React.ReactNode;
  children: React.ReactNode;
  hover?: boolean;
  onClick?: () => void;
}

export default function Card({
  title,
  subtitle,
  className,
  bodyClassName,
  footer,
  children,
  hover = false,
  onClick,
}: CardProps) {
  return (
    <div
      className={cn(
        "bg-white rounded-xl border border-slate-200 overflow-hidden",
        hover && "card-hover cursor-pointer",
        onClick && "cursor-pointer",
        className
      )}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      {(title || subtitle) && (
        <div className="px-6 pt-6 pb-3">
          {title && (
            <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
          )}
        </div>
      )}
      <div className={cn("px-6 py-4", bodyClassName)}>{children}</div>
      {footer && (
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100">
          {footer}
        </div>
      )}
    </div>
  );
}
