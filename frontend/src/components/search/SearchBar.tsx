"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import Button from "@/components/ui/Button";

interface SearchBarProps {
  placeholder?: string;
  defaultValue?: string;
  size?: "sm" | "md" | "lg";
  onSearch?: (query: string) => void;
  className?: string;
}

export default function SearchBar({
  placeholder = "Cerca tra le leggi edilizie...",
  defaultValue = "",
  size = "md",
  onSearch,
  className = "",
}: SearchBarProps) {
  const [query, setQuery] = useState(defaultValue);
  const router = useRouter();

  const handleSearch = useCallback(() => {
    const trimmed = query.trim();
    if (!trimmed) return;

    if (onSearch) {
      onSearch(trimmed);
    } else {
      router.push(`/cerca?q=${encodeURIComponent(trimmed)}`);
    }
  }, [query, router, onSearch]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const sizeStyles = {
    sm: "text-sm py-2 px-4",
    md: "text-base py-3 px-5",
    lg: "text-lg py-4 px-6",
  };

  return (
    <div className={`flex gap-2 ${className}`}>
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="text-slate-400" size={size === "lg" ? 24 : 20} />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`w-full pl-11 pr-4 rounded-xl border border-slate-300 bg-white text-slate-900 placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            transition-all duration-200 shadow-sm ${sizeStyles[size]}`}
          aria-label="Cerca leggi"
        />
      </div>
      <Button onClick={handleSearch} size={size} leftIcon={<Search size={18} />}>
        Cerca
      </Button>
    </div>
  );
}
