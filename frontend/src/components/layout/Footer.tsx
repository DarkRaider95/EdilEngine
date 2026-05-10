import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 mt-auto">
      <div className="container-wide py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-lg font-bold text-white mb-3">
              Edil<span className="text-primary-400">Engine</span>
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Sistema intelligente per navigare le leggi italiane
              dell&apos;edilizia. Ricerca normativa, incentivi, vincoli
              territoriali e chatbot RAG con AI.
            </p>
          </div>

          {/* Link rapidi */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Navigazione
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/cerca"
                  className="hover:text-primary-400 transition-colors"
                >
                  Cerca Leggi
                </Link>
              </li>
              <li>
                <Link
                  href="/categorie"
                  className="hover:text-primary-400 transition-colors"
                >
                  Categorie
                </Link>
              </li>
              <li>
                <Link
                  href="/incentivi"
                  className="hover:text-primary-400 transition-colors"
                >
                  Incentivi
                </Link>
              </li>
              <li>
                <Link
                  href="/vincoli"
                  className="hover:text-primary-400 transition-colors"
                >
                  Vincoli Territoriali
                </Link>
              </li>
              <li>
                <Link
                  href="/chat"
                  className="hover:text-primary-400 transition-colors"
                >
                  Chatbot RAG
                </Link>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Informazioni
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/guida-personalizzata"
                  className="hover:text-primary-400 transition-colors"
                >
                  Guida Personalizzata
                </Link>
              </li>
              <li>
                <a
                  href="/api/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary-400 transition-colors"
                >
                  API Docs (Swagger)
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-800 text-center text-sm text-slate-500">
          &copy; {new Date().getFullYear()} EdilEngine. Tutti i diritti riservati.
        </div>
      </div>
    </footer>
  );
}
