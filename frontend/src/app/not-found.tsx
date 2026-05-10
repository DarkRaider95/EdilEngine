import Link from "next/link";
import Button from "@/components/ui/Button";
import { FileQuestion } from "lucide-react";

export default function NotFound() {
  return (
    <div className="container-page py-20">
      <div className="max-w-lg mx-auto text-center">
        <FileQuestion className="w-16 h-16 text-slate-300 mx-auto mb-6" />
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Pagina non trovata
        </h1>
        <p className="text-lg text-slate-600 mb-8">
          La pagina che stai cercando non esiste o è stata spostata.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/">
            <Button variant="primary" size="md">
              Torna alla Home
            </Button>
          </Link>
          <Link href="/cerca">
            <Button variant="outline" size="md">
              Cerca nelle leggi
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
