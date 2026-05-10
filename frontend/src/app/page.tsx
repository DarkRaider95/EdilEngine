import Link from "next/link";
import {
  Search,
  BookOpen,
  Gift,
  MapPin,
  MessageCircle,
  Compass,
  ArrowRight,
  FileText,
  Database,
  Zap,
} from "lucide-react";
import SearchBar from "@/components/search/SearchBar";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero-gradient text-white">
        <div className="container-page py-20 lg:py-28">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6 animate-fade-in">
              Edil<span className="text-green-300">Engine</span>
            </h1>
            <p className="text-lg sm:text-xl text-primary-100 mb-10 animate-fade-in-delay-1 max-w-2xl mx-auto leading-relaxed">
              Naviga le leggi italiane dell&apos;edilizia con l&apos;intelligenza
              artificiale. Ricerca normativa, incentivi, vincoli territoriali e
              chatbot RAG.
            </p>

            {/* Central Search Bar */}
            <div className="animate-fade-in-delay-2 max-w-xl mx-auto">
              <SearchBar
                placeholder="Cerca leggi, decreti, regolamenti..."
                size="lg"
              />
            </div>

            {/* Quick stats */}
            <div className="mt-12 flex flex-wrap justify-center gap-6 text-sm text-primary-200 animate-fade-in-delay-2">
              <span className="flex items-center gap-1.5">
                <Database className="w-4 h-4" />
                Database normativo completo
              </span>
              <span className="flex items-center gap-1.5">
                <Zap className="w-4 h-4" />
                Ricerca semantica AI
              </span>
              <span className="flex items-center gap-1.5">
                <MessageCircle className="w-4 h-4" />
                Chatbot RAG integrato
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links Cards */}
      <section className="container-wide -mt-16 relative z-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              href: "/cerca",
              icon: Search,
              title: "Cerca Leggi",
              desc: "Ricerca full-text e semantica su tutte le normative edilizie italiane.",
              color: "text-primary-600",
              bg: "bg-primary-50",
            },
            {
              href: "/incentivi",
              icon: Gift,
              title: "Incentivi",
              desc: "Trova bonus, detrazioni e agevolazioni per il tuo progetto edilizio.",
              color: "text-green-600",
              bg: "bg-green-50",
            },
            {
              href: "/vincoli",
              icon: MapPin,
              title: "Vincoli",
              desc: "Verifica i vincoli urbanistici e territoriali del tuo comune.",
              color: "text-amber-600",
              bg: "bg-amber-50",
            },
            {
              href: "/chat",
              icon: MessageCircle,
              title: "Chatbot RAG",
              desc: "Chiedi chiarimenti normativi al nostro assistente AI.",
              color: "text-primary-600",
              bg: "bg-primary-50",
            },
          ].map((card) => {
            const Icon = card.icon;
            return (
              <Link key={card.href} href={card.href}>
                <Card hover className="h-full shadow-lg">
                  <div className="flex flex-col items-center text-center gap-3">
                    <div className={`p-3 rounded-xl ${card.bg}`}>
                      <Icon className={`w-7 h-7 ${card.color}`} />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {card.title}
                    </h3>
                    <p className="text-sm text-slate-600">{card.desc}</p>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Come funziona */}
      <section className="container-page py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
            Come funziona
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Tre semplici passi per navigare la normativa edilizia italiana.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              step: "01",
              icon: Search,
              title: "Cerca la normativa",
              desc: "Inserisci le parole chiave o la domanda. Usa la ricerca semantica per risultati più pertinenti grazie all'AI.",
            },
            {
              step: "02",
              icon: BookOpen,
              title: "Approfondisci",
              desc: "Esplora il testo completo, le categorie correlate e i riferimenti normativi collegati.",
            },
            {
              step: "03",
              icon: Compass,
              title: "Ottieni la guida",
              desc: "Compila il form con i dettagli del tuo progetto per ricevere una guida personalizzata passo-passo.",
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="relative flex flex-col items-center text-center p-8"
              >
                <div className="text-5xl font-extrabold text-primary-100 mb-4 select-none">
                  {item.step}
                </div>
                <div className="p-3 rounded-xl bg-primary-50 mb-4">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA Guide */}
      <section className="bg-slate-100">
        <div className="container-page py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Pronto a iniziare il tuo progetto?
            </h2>
            <p className="text-lg text-slate-600 mb-8">
              Genera una guida personalizzata per il tuo intervento edilizio in
              pochi secondi.
            </p>
            <Link href="/guida-personalizzata">
              <Button size="lg" rightIcon={<ArrowRight size={20} />}>
                Vai alla Guida Personalizzata
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer section - Features */}
      <section className="container-page py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: FileText,
              title: "Normativa aggiornata",
              desc: "Database costantemente aggiornato con leggi, decreti e regolamenti edilizi.",
            },
            {
              icon: Database,
              title: "Ricerca AI",
              desc: "Ricerca semantica basata su embeddings per trovare i contenuti più pertinenti.",
            },
            {
              icon: MessageCircle,
              title: "Chatbot RAG",
              desc: "Assistente AI con accesso diretto alle fonti normative per risposte affidabili.",
            },
            {
              icon: Compass,
              title: "Guide personalizzate",
              desc: "Genera guide passo-passo basate su posizione, intervento e caratteristiche del progetto.",
            },
          ].map((feature) => {
            const Icon = feature.icon;
            return (
              <div key={feature.title} className="flex gap-3">
                <div className="flex-shrink-0 p-2 rounded-lg bg-primary-50">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 mb-1">
                    {feature.title}
                  </h4>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </>
  );
}
