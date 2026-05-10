"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="container-page py-20">
      <div className="max-w-lg mx-auto text-center">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Qualcosa è andato storto
        </h1>
        <p className="text-lg text-slate-600 mb-8">
          Si è verificato un errore imprevisto. Riprova o torna alla home.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center px-5 py-2.5 bg-primary-600 text-white rounded-lg font-medium
              hover:bg-primary-700 transition-colors"
          >
            Riprova
          </button>
          <a
            href="/"
            className="inline-flex items-center justify-center px-5 py-2.5 border-2 border-slate-300 text-slate-700 rounded-lg font-medium
              hover:bg-slate-100 transition-colors"
          >
            Torna alla Home
          </a>
        </div>
      </div>
    </div>
  );
}
