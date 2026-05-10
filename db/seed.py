"""
EdilEngine Data Loader - Popola il database con dati reali italiani sull'edilizia.

Esecuzione:
  python db/seed.py                     # dal backend container
  docker compose exec backend python db/seed.py   # da fuori

Lo script è idempotente: può essere eseguito più volte senza duplicare i dati.
"""

import asyncio
import hashlib
import sys
import os
import uuid
from datetime import date

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ============================================================================
# DATI REALI ITALIANI SULL'EDILIZIA
# ============================================================================

CATEGORIE = [
    {"id": "c0000001-0000-0000-0000-000000000001", "nome": "Urbanistica"},
    {"id": "c0000001-0000-0000-0000-000000000002", "nome": "Edilizia"},
    {"id": "c0000001-0000-0000-0000-000000000003", "nome": "Incentivi fiscali"},
    {"id": "c0000001-0000-0000-0000-000000000004", "nome": "Sismica"},
    {"id": "c0000001-0000-0000-0000-000000000005", "nome": "Ambiente ed energia"},
    {"id": "c0000001-0000-0000-0000-000000000006", "nome": "Impianti"},
    {"id": "c0000001-0000-0000-0000-000000000007", "nome": "Appalti pubblici"},
    {"id": "c0000001-0000-0000-0000-000000000008", "nome": "Procedimento amministrativo"},
]

LEGGI = [
    {
        "id": "a0000001-0000-0000-0000-000000000001",
        "titolo": "Testo unico delle norme per l'edilizia",
        "tipo": "D.P.R.",
        "numero": "D.P.R. 380/2001",
        "data_emanazione": date(2001, 8, 6),
        "data_pubblicazione": date(2001, 9, 18),
        "data_vigore": date(2001, 10, 8),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:2001-08-06;380",
        "categorie": ["Urbanistica", "Edilizia"],
        "testo_completo": """TESTO UNICO DELLE NORME PER L'EDILIZIA (D.P.R. 380/2001)

Il Testo Unico dell'Edilizia è la principale normativa di riferimento per l'attività edilizia in Italia. Regola i procedimenti di autorizzazione per interventi edilizi, definendo le tipologie di intervento e i relativi titoli abilitativi.

ART. 3 - Definizioni degli interventi edilizi
Gli interventi edilizi si distinguono in:
a) manutenzione ordinaria: interventi che riguardano le opere di riparazione, rinnovamento e sostituzione delle finiture degli edifici e quelle necessarie per integrare o mantenere in efficienza gli impianti esistenti;
b) manutenzione straordinaria: le opere e le modifiche necessarie per rinnovare e sostituire parti anche strutturali degli edifici, nonché per realizzare e integrare i servizi igienico-sanitari e tecnologici;
c) restauro e risanamento conservativo: interventi finalizzati a conservare l'organismo edilizio e ad assicurarne la funzionalità;
d) ristrutturazione edilizia: interventi che trasformano l'organismo edilizio mediante un insieme sistematico di opere;
e) nuova costruzione: costruzione di nuovi edifici;
f) interventi di recupero di cui alla legge 457/1978.

ART. 6 - Titoli abilitativi
1. Gli interventi di manutenzione ordinaria sono realizzabili senza alcun titolo abilitativo.
2. Per gli interventi di manutenzione straordinaria è richiesta la CILA (Comunicazione di Inizio Lavori Asseverata).
3. Per gli interventi di restauro e risanamento conservativo è richiesta la SCIA (Segnalazione Certificata di Inizio Attività).
4. Per gli interventi di ristrutturazione edilizia è richiesta la SCIA.
5. Per gli interventi di nuova costruzione è richiesto il Permesso di Costruire.

ART. 10 - Permesso di costruire
Il permesso di costruire è richiesto per:
a) gli interventi di nuova costruzione;
b) gli interventi di ristrutturazione urbanistica;
c) gli interventi di ristrutturazione edilizia che portino a volumi diversi da quelli preesistenti.

ART. 22 - CILA
La Comunicazione di Inizio Lavori Asseverata è presentata al Comune prima dell'inizio dei lavori e contiene l'elenco degli interventi da realizzare e la loro conformità alle norme urbanistiche ed edilizie.

ART. 22-bis - SCIA
La SCIA è presentata al Comune e contiene la descrizione degli interventi e la certificazione di conformità alle norme vigenti. I lavori possono iniziare dopo la presentazione della SCIA.""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000002",
        "titolo": "Decreto Rilancio - Superbonus 110%",
        "tipo": "Decreto-legge",
        "numero": "D.L. 34/2020",
        "data_emanazione": date(2020, 5, 19),
        "data_pubblicazione": date(2020, 5, 19),
        "data_vigore": date(2020, 5, 19),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2020-05-19;34",
        "categorie": ["Incentivi fiscali", "Edilizia"],
        "testo_completo": """DECRETO-LEGGE 19 MAGGIO 2020, N. 34 (DECRETO RILANCIO) - SUPERBONUS 110%

Il Decreto Rilancio introduce il Superbonus, una detrazione fiscale del 110% per interventi di efficientamento energetico e riduzione del rischio sismico degli edifici.

ART. 119 - Detrazione per interventi di efficientamento energetico
1. E' riconosciuta una detrazione dall'imposta lorda, fino a un importo massimo di 60.000 euro, per gli interventi di efficientamento energetico degli edifici esistenti.
2. La detrazione è del 110% delle spese sostenute per:
   a) interventi di isolamento termico delle superfici opache verticali e orizzontali;
   b) sostituzione degli impianti di climatizzazione invernale esistenti con impianti centralizzati;
   c) interventi antisismici.

INTERVENTI TRAINANTI (c.d. "interventi trainanti"):
- Isolamento termico delle superfici opache (cappotto termico)
- Sostituzione degli impianti di climatizzazione invernale
- Interventi antisismici su edifici ubicati nelle zone sismiche 1, 2 e 3

INTERVENTI TRAINATI (c.d. "interventi trainati"):
- Sostituzione di finestre e infissi
- Installazione di pannelli solari fotovoltaici
- Installazione di colonnine di ricarica per veicoli elettrici
- Sostituzione di impianti di climatizzazione invernale

CONDIZIONI PER L'ACCESSO:
- L'intervento deve essere realizzato su edifici esistenti
- Miglioramento di almeno due classi energetiche (o classe massima)
- Asseverazione da parte di un tecnico abilitato
- Visto di conformità da parte di un ENAC""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000003",
        "titolo": "Ecobonus - Detrazione per riqualificazione energetica",
        "tipo": "Legge",
        "numero": "L. 276/2013 e D.M. 26/2015",
        "data_emanazione": date(2013, 8, 3),
        "data_pubblicazione": date(2013, 8, 28),
        "data_vigore": date(2013, 9, 17),
        "autorita": "Stato",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/ecobonus",
        "categorie": ["Incentivi fiscali", "Ambiente ed energia"],
        "testo_completo": """ECOBONUS - DETRAZIONE PER INTERVENTI DI RIQUALIFICAZIONE ENERGETICA DEGLI EDIFICI

L'Ecobonus è una detrazione fiscale per interventi di riqualificazione energetica degli edifici esistenti. La detrazione varia dal 50% al 65% a seconda del tipo di intervento.

INTERVENTI DETRAIBILI AL 65%:
- Sostituzione di impianti di climatizzazione invernale con impianti a basso consumo
- Installazione di pannelli solari termici per la produzione di acqua calda
- Sostituzione di finestre e infissi (in combinazione con altri interventi)
- Coibentazione di pareti e coperture (isolamento termico)
- Sistemi di building automation per il controllo dei consumi

INTERVENTI DETRAIBILI AL 50%:
- Sostituzione di finestre e infissi (da solo)
- Installazione di schermature solari
- Sostituzione di impianti di riscaldamento con pompe di calore

REQUISITI:
- Interventi su edifici esistenti
- Miglioramento delle prestazioni energetiche
- Asseverazione da parte di un tecnico abilitato
- Rispetto dei requisiti minimi di efficienza energetica

FRUIZIONE:
- La detrazione è ripartita in 10 quote annuali di pari importo
- È possibile cedere il credito d'imposta o ottenere uno sconto in fattura (opzione "sconto sul prezzo")""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000004",
        "titolo": "Sismabonus - Detrazione per interventi antisismici",
        "tipo": "Decreto-legge",
        "numero": "D.L. 63/2013",
        "data_emanazione": date(2013, 6, 4),
        "data_pubblicazione": date(2013, 6, 4),
        "data_vigore": date(2013, 6, 4),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2013-06-04;63",
        "categorie": ["Sismica", "Incentivi fiscali"],
        "testo_completo": """SISMABONUS - DETRAZIONE PER INTERVENTI ANTISISMICI

Il Sismabonus è una detrazione fiscale per gli interventi di riduzione del rischio sismico degli edifici. La detrazione varia dal 50% all'85% a seconda della classe di rischio e della zona sismica.

ZONE SISMICHE DI APPLICAZIONE:
- Zona 1 (alta sismicità): ICPC > 100
- Zona 2 (media sismicità): ICPC 75-100
- Zona 3 (bassa sismicità): ICPC 60-75

ALIQUOTE DETRAZIONE:
- 50% per interventi che migliorano di 1 classe di rischio
- 70% per interventi che migliorano di 2 classi di rischio
- 80% per interventi che migliorano di 3 classi di rischio (zona sismica 1 e 2)
- 85% per interventi su edifici in zona sismica 1 e 2 con miglioramento di 2 o più classi

SPESA MASSIMA:
- 96.000 euro per unità immobiliare per gli interventi su parti comuni
- 48.000 euro per unità immobiliare per gli interventi su singole unità

CONDIZIONI:
- Edifici ubicati in zona sismica 1, 2 o 3
- Asseverazione da parte di un ingegnere strutturale
- Classificazione del rischio sismico prima e dopo l'intervento
- Visto di conformità dell'ENAC""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000005",
        "titolo": "Bonus Facciate - Detrazione per interventi sulle facciate",
        "tipo": "Legge",
        "numero": "L. 205/2017, art. 1, c. 219",
        "data_emanazione": date(2017, 12, 27),
        "data_pubblicazione": date(2017, 12, 29),
        "data_vigore": date(2018, 1, 1),
        "autorita": "Stato",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/bonus-facciate",
        "categorie": ["Incentivi fiscali", "Edilizia"],
        "testo_completo": """BONUS FACCIATE - DETRAZIONE PER INTERVENTI SULLE FACCIATE DEGLI EDIFICI

Il Bonus Facciate è una detrazione fiscale del 60% (90% per interventi in zone sismiche) per le spese sostenute per interventi di recupero o restauro della facciata degli edifici esistenti.

INTERVENTI AMMESSI:
- Pulitura delle facciate
- Pitturazione delle facciate
- Sostituzione di elementi decorativi
- Ripristino di balconi e cornici
- Interventi su grondaie e pluviali
- Sistemazione di scale esterne

REQUISITI:
- L'edificio deve essere esistente (non nuovo)
- L'intervento deve riguardare la facciata esterna visibile
- L'edificio deve essere situato in zone A o B del piano regolatore (centri storici)
- Per il 90%: edificio in zona sismica 1, 2 o 3 con miglioramento sismico

SPESA MASSIMA:
- Non c'è un limite massimo di spesa
- La detrazione è ripartita in 10 quote annuali

SCADENZA:
- 31 dicembre 2024 (prorogato dalla Legge di Bilancio 2024)""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000006",
        "titolo": "Bonus Verde - Detrazione per interventi di sistemazione a verde",
        "tipo": "Legge",
        "numero": "L. 205/2017, art. 1, c. 224",
        "data_emanazione": date(2017, 12, 27),
        "data_pubblicazione": date(2017, 12, 29),
        "data_vigore": date(2018, 1, 1),
        "autorita": "Stato",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/bonus-verde",
        "categorie": ["Incentivi fiscali", "Ambiente ed energia"],
        "testo_completo": """BONUS VERDE - DETRAZIONE PER INTERVENTI DI SISTEMAZIONE A VERDE

Il Bonus Verde è una detrazione fiscale del 36% per le spese sostenute per la sistemazione a verde di aree scoperte pertinenziali o di terrazze condominiali.

INTERVENTI AMMESSI:
- Sistemazione a verde di giardini e cortili
- Realizzazione di tetti verdi e giardini pensili
- Installazione di impianti di irrigazione
- Piantumazione di alberi e arbusti
- Realizzazione di pozzi e sistemi di raccolta acqua
- Sistemazione di terrazze e balconi con piante e fiori

SPESA MASSIMA:
- 5.000 euro per unità immobiliare (detrazione massima: 1.800 euro)
- La detrazione è ripartita in 10 quote annuali

REQUISITI:
- L'intervento deve riguardare aree scoperte pertinenziali all'immobile
- Le aree devono essere adibite a verde
- Non sono ammessi interventi su aree comuni non pertinenziali""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000007",
        "titolo": "Conto Termico 2.0 - Incentivo per efficientamento energetico",
        "tipo": "Decreto Ministeriale",
        "numero": "D.M. 16/2016",
        "data_emanazione": date(2016, 2, 16),
        "data_pubblicazione": date(2016, 3, 16),
        "data_vigore": date(2016, 4, 1),
        "autorita": "MASE",
        "url_fonte": "https://www.gse.it/servizi-per-te/conto-termico",
        "categorie": ["Incentivi fiscali", "Ambiente ed energia"],
        "testo_completo": """CONTO TERMICO 2.0 - INCENTIVO PER INTERVENTI DI EFFICIENTAMENTO ENERGETICO

Il Conto Termico è un incentivo gestito dal GSE (Gestore Servizi Energetici) per interventi di efficientamento energetico e produzione di energia termica da fonti rinnovabili.

INTERVENTI AMMESSI:
- Installazione di pompe di calore
- Installazione di caldaie a condensazione
- Sostituzione di impianti di climatizzazione
- Installazione di impianti solari termici
- Interventi di isolamento termico (cappotto)
- Sistemi di building automation
- Colonnine di ricarica per veicoli elettrici

ENTITÀ DELL'INCENTIVO:
- Variabile in base al tipo di intervento e alla zona climatica
- Durata dell'incentivo: da 2 a 5 anni
- Importo calcolato in base al risparmio energetico ottenuto
- Non è una detrazione fiscale ma un contributo a fondo perduto

COME ACCEDERE:
- Presentazione della domanda al GSE entro 60 giorni dalla fine dei lavori
- Asseverazione da parte di un tecnico abilitato
- Documentazione fotografica degli interventi""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000008",
        "titolo": "Norme sismiche - Classificazione e prevenzione",
        "tipo": "Legge",
        "numero": "L. 64/1974 e O.P.C.M. 3274/2003",
        "data_emanazione": date(1974, 2, 2),
        "data_pubblicazione": date(1974, 2, 15),
        "data_vigore": date(2003, 3, 20),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1974-02-02;64",
        "categorie": ["Sismica", "Edilizia"],
        "testo_completo": """NORME SISMICHE - CLASSIFICAZIONE E PREVENZIONE DEL RISCHIO SISMICO

La Legge 64/1974 e l'Ordinanza del Presidente del Consiglio dei Ministri n. 3274/2003 costituiscono il quadro normativo per la classificazione sismica del territorio italiano e le norme tecniche per le costruzioni in zona sismica.

CLASSIFICAZIONE SISMICA DELL'ITALIA:
- Zona 1 (alta sismicità): comprende i comuni con accelerazione massima attesa > 0.25g
- Zona 2 (media sismicità): accelerazione tra 0.15g e 0.25g
- Zona 3 (bassa sismicità): accelerazione tra 0.05g e 0.15g
- Zona 4 (sismicità molto bassa): accelerazione < 0.05g

NORME TECNICHE PER LE COSTRUZIONI (NTC 2018):
- Requisiti di sicurezza per le costruzioni nuove
- Criteri per la valutazione della sicurezza delle costruzioni esistenti
- Metodi di progettazione per azioni sismiche
- Categorie di sottosuolo (A, B, C, D, E)

OBBLIGHI PER LE COSTRUZIONI IN ZONA SISMICA:
- Progetto strutturale redatto da ingegnere iscritto all'albo
- Verifica di sicurezza per azioni sismiche
- Direzione lavori di ingegnere strutturale
- Collaudo statico per edifici strategici

VINCOLI PER INTERVENTI EDILIZI:
- In zona sismica 1 e 2: obbligo di miglioramento sismico per ogni intervento di ristrutturazione
- In zona sismica 3: valutazione della vulnerabilità sismica per interventi di ristrutturazione
- In zona sismica 4: nessun obbligo specifico""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000009",
        "titolo": "Decreto legislativo sull'efficienza energetica degli edifici",
        "tipo": "Decreto legislativo",
        "numero": "D.Lgs. 192/2005",
        "data_emanazione": date(2005, 8, 19),
        "data_pubblicazione": date(2005, 9, 14),
        "data_vigore": date(2005, 10, 4),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-08-19;192",
        "categorie": ["Ambiente ed energia", "Edilizia"],
        "testo_completo": """DECRETO LEGISLATIVO 19 AGOSTO 2005, N. 192 - ATTUAZIONE DELLA DIRETTIVA 2002/91/CE SULL'EFFICIENZA ENERGETICA NELLE COSTRUZIONI

Il D.Lgs. 192/2005 recepisce la direttiva europea sull'efficienza energetica degli edifici e stabilisce i requisiti minimi di prestazione energetica per gli edifici nuovi e ristrutturati.

REQUISITI MINIMI DI PRESTAZIONE ENERGETICA:
- Edifici nuovi: rispetto dei valori limite di trasmittanza termica
- Edifici ristrutturati: miglioramento della classe energetica di almeno due livelli
- Impianti termici: rendimento minimo stagionale
- Impianti di climatizzazione: efficienza energetica minima

ATTESTATO DI PRESTAZIONE ENERGETICA (APE):
- Obbligatorio per tutti gli edifici alla vendita o alla locazione
- Obbligatorio per gli edifici pubblici con superficie utile > 250 mq
- Validità: 10 anni
- Redatto da un tecnico abilitato (ingegnere, architetto, perito industriale)

CLASSI ENERGETICHE:
- A4: edificio a energia quasi zero (NZEB)
- A3: alta efficienza energetica
- A2: buona efficienza energetica
- A1: discreta efficienza energetica
- B: media efficienza energetica
- C: sufficiente efficienza energetica
- D: bassa efficienza energetica
- E: molto bassa efficienza energetica
- F: scarsa efficienza energetica
- G: pessima efficienza energetica""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000010",
        "titolo": "Bonus Casa - Detrazione per interventi di recupero edilizio",
        "tipo": "Legge",
        "numero": "L. 689/1981 e successive modificazioni",
        "data_emanazione": date(1981, 11, 23),
        "data_pubblicazione": date(1981, 12, 10),
        "data_vigore": date(1981, 12, 28),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1981-11-23;689",
        "categorie": ["Incentivi fiscali", "Edilizia"],
        "testo_completo": """BONUS CASA (EX DETRAZIONE 36%/50%) - DETRAZIONE PER INTERVENTI DI RECUPERO DEL PATRIMONIO EDILIZIO

Il Bonus Casa (già noto come detrazione 36% o 50%) è una detrazione fiscale per interventi di recupero del patrimonio edilizio e per la realizzazione di box auto pertinenziali.

ALIQUOTA DETRAZIONE:
- 50% per interventi di recupero del patrimonio edilizio (fino al 31 dicembre 2024)
- 36% per interventi di manutenzione ordinaria e straordinaria

INTERVENTI AMMESSI:
- Manutenzione straordinaria
- Restauro e risanamento conservativo
- Ristrutturazione edilizia
- Realizzazione di box auto pertinenziali
- Eliminazione di barriere architettoniche
- Installazione di impianti tecnologici
- Adozione di misure di sicurezza contro la criminalità

SPESA MASSIMA:
- 96.000 euro per unità immobiliare (detrazione massima: 48.000 euro al 50%)
- La detrazione è ripartita in 10 quote annuali

OPZIONI ALTERNATIVE:
- Sconto in fattura: il contribuente può cedere il credito d'imposta all'impresa edile che applica uno sconto in fattura
- Cessione del credito: il contribuente può cedere il credito d'imposta a terzi (banche, intermediari finanziari)

REQUISITI:
- Pagamento con bonifico bancario o postale dedicato
- Conservazione della documentazione per 5 anni
- Comunicazione all'Agenzia delle Entrate (opzione sconto/cessione)""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000011",
        "titolo": "Decreto legislativo sulle energie rinnovabili",
        "tipo": "Decreto legislativo",
        "numero": "D.Lgs. 28/2011",
        "data_emanazione": date(2011, 3, 3),
        "data_pubblicazione": date(2011, 3, 24),
        "data_vigore": date(2011, 4, 13),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2011-03-03;28",
        "categorie": ["Ambiente ed energia"],
        "testo_completo": """DECRETO LEGISLATIVO 3 MARZO 2011, N. 28 - ATTUAZIONE DELLA DIRETTIVA 2009/28/CE SULLE ENERGIE RINNOVABILI

Il D.Lgs. 28/2011 recepisce la direttiva europea sulle energie rinnovabili e stabilisce le norme per la promozione dell'uso delle fonti di energia rinnovabile.

OBIETTIVI NAZIONALI:
- 17% di energia da fonti rinnovabili sui consumi totali al 2020
- 26,4% di energia elettrica da fonti rinnovabili
- 17% di energia nel settore riscaldamento/raffreddamento
- 10% di energia da fonti rinnovabili nei trasporti

IMPIANTI FOTOVOLTAICI:
- Autorizzazione semplificata per impianti fino a 20 kW (DIA/SCIA)
- Autorizzazione unica per impianti superiori a 20 kW
- Connessione alla rete elettrica obbligatoria per i gestori di rete
- Scambio sul posto per impianti fino a 200 kW

IMPIANTI GEOTERMICI:
- Libera installazione per pompe di calore con potenza termica < 50 kW
- DIA/SCIA per potenza tra 50 kW e 500 kW
- Autorizzazione unica per potenza superiore a 500 kW""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000012",
        "titolo": "Legge sull'energia - Norme per l'energia elettrica e il gas",
        "tipo": "Legge",
        "numero": "L. 10/1991",
        "data_emanazione": date(1991, 1, 9),
        "data_pubblicazione": date(1991, 1, 16),
        "data_vigore": date(1991, 1, 31),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1991-01-09;10",
        "categorie": ["Ambiente ed energia", "Impianti"],
        "testo_completo": """LEGGE 9 GENNAIO 1991, N. 10 - NORME PER L'ATTUAZIONE DEL PIANO ENERGETICO NAZIONALE IN MATERIA DI ENERGIA ELETTRICA E GAS

La Legge 10/1991 stabilisce le norme per l'uso razionale dell'energia, l'attuazione del piano energetico nazionale e le disposizioni in materia di energia elettrica e gas.

ART. 4 - REQUISITI DI EFFICIENZA ENERGETICA
I nuovi edifici e gli edifici sottoposti a ristrutturazione devono rispettare i requisiti minimi di efficienza energetica stabiliti dal D.Lgs. 192/2005 e successive modificazioni.

ART. 5 - CERTIFICAZIONE ENERGETICA
Gli edifici devono essere dotati di attestato di certificazione energetica (APE) alla vendita o alla locazione.

ART. 26 - IMPIANTI TERMICI
Gli impianti termici devono essere progettati, installati e manutenuti in conformità alle norme UNI e alle disposizioni del D.P.R. 412/1993.

ART. 27 - MANUTENZIONE DEGLI IMPIANTI
I proprietari o gli amministratori degli edifici devono sottoporre gli impianti termici a manutenzione periodica e al controllo del rendimento di combustione.

ART. 28 - LIBRETTO DI CENTRALE TERMICA
Per gli impianti termici centralizzati è obbligatorio il libretto di centrale termica, che deve essere compilato e aggiornato a cura del responsabile dell'impianto.""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000013",
        "titolo": "Regolamento sugli impianti termici",
        "tipo": "Decreto del Presidente della Repubblica",
        "numero": "D.P.R. 412/1993",
        "data_emanazione": date(1993, 8, 26),
        "data_pubblicazione": date(1993, 9, 30),
        "data_vigore": date(1993, 10, 21),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1993-08-26;412",
        "categorie": ["Impianti", "Edilizia"],
        "testo_completo": """D.P.R. 26 AGOSTO 1993, N. 412 - REGOLAMENTO RECANTE NORME PER LA PROGETTAZIONE, L'INSTALLAZIONE E LA MANUTENZIONE DEGLI IMPIANTI TERMICI

Il D.P.R. 412/1993 è il regolamento di riferimento per gli impianti termici degli edifici. Stabilisce le norme per la progettazione, l'installazione, l'esercizio e la manutenzione degli impianti termici.

ZONE CLIMATICHE DELL'ITALIA:
- Zona A: comuni con gradi giorno ≤ 600 (Lampedusa, Linosa)
- Zona B: comuni con gradi giorno 601-900 (Palermo, Reggio Calabria)
- Zona C: comuni con gradi giorno 901-1400 (Roma, Napoli, Bari)
- Zona D: comuni con gradi giorno 1401-2100 (Milano, Torino, Bologna)
- Zona E: comuni con gradi giorno 2101-3000 (Bolzano, Belluno)
- Zona F: comuni con gradi giorno > 3000 (alta montagna)

PERIODI DI ACCENSIONE DEGLI IMPIANTI TERMICI:
- Zona A: 1° dicembre - 15 marzo, max 6 ore/giorno
- Zona B: 1° dicembre - 31 marzo, max 8 ore/giorno
- Zona C: 15 novembre - 31 marzo, max 10 ore/giorno
- Zona D: 1° novembre - 15 aprile, max 12 ore/giorno
- Zona E: 15 ottobre - 15 aprile, max 14 ore/giorno
- Zona F: senza limitazioni

TEMPERATURE MASSIME CONSENTITE:
- 20°C con tolleranza di 2°C per tutti gli edifici
- 18°C per gli edifici adibiti ad attività commerciali
- 22°C per le piscine e gli edifici adibiti ad attività sportive""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000014",
        "titolo": "Codice dei contratti pubblici",
        "tipo": "Decreto legislativo",
        "numero": "D.Lgs. 36/2023",
        "data_emanazione": date(2023, 3, 31),
        "data_pubblicazione": date(2023, 4, 14),
        "data_vigore": date(2023, 7, 1),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2023-03-31;36",
        "categorie": ["Appalti pubblici"],
        "testo_completo": """CODICE DEI CONTRATTI PUBBLICI (D.LGS. 36/2023)

Il nuovo Codice dei Contratti Pubblici sostituisce il D.Lgs. 50/2016 e disciplina gli appalti pubblici di lavori, servizi e forniture.

PRINCIPI FONDAMENTALI:
- Libera concorrenza
- Parità di trattamento
- Trasparenza e tracciabilità
- Proporzionalità
- Rotazione degli inviti

PROCEDURE DI AFFIDAMENTO:
- Affidamento diretto: fino a 5.000 euro
- Invito diretto: fino a 150.000 euro per servizi e forniture, fino a 1.000.000 euro per lavori
- Procedura negoziata: sopra le soglie dell'invito diretto
- Procedura aperta: sopra le soglie comunitarie

SOGLIE COMUNITARIE PER I LAVORI:
- 5.382.000 euro per i lavori pubblici
- 140.000 euro per i servizi e le forniture

REQUISITI DI PARTICOLARIZZAZIONE:
- SOA (Società Organismo di Attestazione) per i lavori sopra 150.000 euro
- Certificato di qualificazione per i servizi e le forniture""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000015",
        "titolo": "Legge sul procedimento amministrativo",
        "tipo": "Legge",
        "numero": "L. 241/1990",
        "data_emanazione": date(1990, 8, 7),
        "data_pubblicazione": date(1990, 8, 18),
        "data_vigore": date(1990, 9, 7),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1990-08-07;241",
        "categorie": ["Procedimento amministrativo"],
        "testo_completo": """LEGGE 7 AGOSTO 1990, N. 241 - NUOVE NORME IN MATERIA DI PROCEDIMENTO AMMINISTRATIVO E DIRITTO DI ACCESSO AI DOCUMENTI AMMINISTRATIVI

La Legge 241/1990 disciplina il procedimento amministrativo, i diritti dei cittadini nei confronti della pubblica amministrazione e l'accesso ai documenti amministrativi.

ART. 2 - DIRITTO ALLA TRASPARENZA
I cittadini hanno diritto di accedere ai documenti amministrativi e di conoscere lo stato dei procedimenti che li riguardano.

ART. 3 - TERMINE DEL PROCEDIMENTO
I procedimenti amministrativi devono concludersi entro 30 giorni dalla data di ricezione della domanda. In mancanza, il silenzio dell'amministrazione vale come accoglimento della domanda (silenzio-assenso).

ART. 5 - COMUNICAZIONE DI AVVIO DEL PROCEDIMENTO
L'amministrazione deve comunicare l'avvio del procedimento ai destinatari e ai controinteressati, indicando il responsabile del procedimento e i termini.

ART. 10 - SILenzio-ASSENSO
Se l'amministrazione non si pronuncia entro il termine di 30 giorni, la domanda si intende accolta (silenzio-assenso), salvo eccezioni specifiche previste dalla legge.

ART. 25 - DIRITTO DI ACCESSO
Chiunque vi abbia un interesse diretto, concreto e attuale può chiedere di accedere ai documenti amministrativi.

APPLICAZIONE ALL'EDILIZIA:
- Permesso di costruire: termine 90 giorni (art. 20 D.P.R. 380/2001)
- SCIA: effetto immediato, l'amministrazione può verificare entro 60 giorni
- CILA: effetto immediato, l'amministrazione può verificare entro 30 giorni""",
    },
    {
        "id": "a0000001-0000-0000-0000-000000000016",
        "titolo": "Detrazione per barriere architettoniche",
        "tipo": "Legge",
        "numero": "L. 67/1989 e L. 13/1989",
        "data_emanazione": date(1989, 3, 21),
        "data_pubblicazione": date(1989, 3, 28),
        "data_vigore": date(1989, 4, 17),
        "autorita": "Stato",
        "url_fonte": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1989-03-21;67",
        "categorie": ["Edilizia", "Incentivi fiscali"],
        "testo_completo": """DETRAZIONE PER L'ELIMINAZIONE DELLE BARRIERE ARCHITETTONICHE

La detrazione per l'eliminazione delle barriere architettoniche è un'agevolazione fiscale per gli interventi finalizzati a superare ed eliminare le barriere architettoniche negli edifici esistenti.

ALIQUOTA E LIMITI:
- Detrazione del 75% delle spese sostenute
- Spesa massima: 96.000 euro per unità immobiliare
- Detrazione massima: 72.000 euro
- Ripartizione in 5 quote annuali

INTERVENTI AMMESSI:
- Installazione di ascensori e montacarichi
- Costruzione di rampe per il superamento di dislivelli
- Ampliamento di porte e vani per il passaggio di sedie a rotelle
- Sostituzione di gradini con rampe
- Installazione di corrimano e maniglioni
- Adattamento di bagni per persone con disabilità
- Installazione di piattaforme elevatrici
- Realizzazione di parcheggi riservati

BENEFICIARI:
- Persone con disabilità (riconosciuta ai sensi della L. 104/1992)
- Familiari delle persone con disabilità
- Condomini per interventi su parti comuni

REQUISITI:
- Interventi su edifici esistenti
- Conformità alla L. 13/1989 e al D.M. 236/1989
- Certificazione medica che attesti la necessità dell'intervento""",
    },
]

INCENTIVI = [
    {
        "id": "b0000001-0000-0000-0000-000000000001",
        "titolo": "Superbonus 110%",
        "descrizione": "Detrazione fiscale del 110% per interventi di efficientamento energetico, riduzione del rischio sismico e rimozione di barriere architettonici. Gli interventi devono essere completati entro il 31 dicembre 2024 per i condomini e il 31 dicembre 2025 per le unità immobiliari unifamiliari. È possibile cedere il credito d'imposta o ottenere uno sconto in fattura dall'impresa esecutrice dei lavori.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "superbonus",
        "aliquota": 110.00,
        "scadenza": date(2025, 12, 31),
        "requisiti": "Interventi trainanti: isolamento termico, sostituzione impianti di climatizzazione, interventi antisismici. Miglioramento di almeno due classi energetiche o classe massima. Asseverazione tecnica e visto di conformità ENAC.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/superbonus",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000002",
        "titolo": "Ecobonus 65%",
        "descrizione": "Detrazione fiscale del 65% per interventi di riqualificazione energetica degli edifici. Include isolamento termico, sostituzione impianti di climatizzazione, installazione di pannelli solari termici e sostituzione di finestre e infissi. La detrazione è ripartita in 10 quote annuali.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "ecobonus",
        "aliquota": 65.00,
        "scadenza": date(2025, 12, 31),
        "requisiti": "Interventi di efficientamento energetico su edifici esistenti. Asseverazione tecnica. Rispetto dei requisiti minimi di efficienza energetica. Pagamento con bonifico bancario dedicato.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/ecobonus",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000003",
        "titolo": "Sismabonus",
        "descrizione": "Detrazione fiscale dal 50% all'85% per interventi di riduzione del rischio sismico degli edifici. La percentuale varia in base alla classe di rischio e alla zona sismica. È cumulabile con il Superbonus per interventi antisismici.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "sismabonus",
        "aliquota": 85.00,
        "scadenza": date(2025, 12, 31),
        "requisiti": "Edifici ubicati in zona sismica 1, 2 o 3. Asseverazione di ingegnere strutturale. Classificazione del rischio sismico prima e dopo l'intervento. Visto di conformità ENAC.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/sismabonus",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000004",
        "titolo": "Bonus Facciate",
        "descrizione": "Detrazione fiscale del 60% (90% in zona sismica) per interventi di recupero o restauro delle facciate degli edifici esistenti. Include pulitura, pitturazione, sostituzione di elementi decorativi e ripristino di balconi.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "bonus-facciate",
        "aliquota": 60.00,
        "scadenza": date(2024, 12, 31),
        "requisiti": "Edificio esistente. Interventi sulla facciata esterna visibile. Edificio in zona A o B del piano regolatore (centro storico). Per il 90%: edificio in zona sismica 1, 2 o 3 con miglioramento sismico.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/bonus-facciate",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000005",
        "titolo": "Bonus Verde",
        "descrizione": "Detrazione fiscale del 36% per la sistemazione a verde di aree scoperte pertinenziali o di terrazze condominiali. Include piantumazione di alberi e arbusti, installazione di impianti di irrigazione e realizzazione di tetti verdi.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "bonus-verde",
        "aliquota": 36.00,
        "scadenza": date(2024, 12, 31),
        "requisiti": "Interventi su aree scoperte pertinenziali all'immobile. Le aree devono essere adibite a verde. Spesa massima 5.000 euro per unità immobiliare.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/bonus-verde",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000006",
        "titolo": "Conto Termico 2.0",
        "descrizione": "Incentivo gestito dal GSE per interventi di efficientamento energetico e produzione di energia termica da fonti rinnovabili. Non è una detrazione fiscale ma un contributo a fondo perduto. Durata da 2 a 5 anni a seconda dell'intervento.",
        "ente_erogatore": "GSE",
        "tipo": "conto-termico",
        "aliquota": None,
        "scadenza": date(2026, 12, 31),
        "requisiti": "Presentazione domanda al GSE entro 60 giorni dalla fine dei lavori. Asseverazione tecnica. Documentazione fotografica degli interventi.",
        "url_fonte": "https://www.gse.it/servizi-per-te/conto-termico",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000007",
        "titolo": "Bonus Casa (detrazione 50%)",
        "descrizione": "Detrazione fiscale del 50% per interventi di recupero del patrimonio edilizio. Include manutenzione straordinaria, restauro e risanamento conservativo, ristrutturazione edilizia, realizzazione di box auto e eliminazione di barriere architettoniche.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "bonus-casa",
        "aliquota": 50.00,
        "scadenza": date(2025, 12, 31),
        "requisiti": "Pagamento con bonifico bancario dedicato. Conservazione della documentazione per 5 anni. Comunicazione all'Agenzia delle Entrate per opzione sconto/cessione.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/bonus-casa",
    },
    {
        "id": "b0000001-0000-0000-0000-000000000008",
        "titolo": "Detrazione barriere architettoniche",
        "descrizione": "Detrazione fiscale del 75% per l'eliminazione delle barriere architettoniche negli edifici esistenti. Include installazione di ascensori, costruzione di rampe, ampliamento di porte e adattamento di bagni per persone con disabilità.",
        "ente_erogatore": "Agenzia delle Entrate",
        "tipo": "barriere-architettoniche",
        "aliquota": 75.00,
        "scadenza": date(2025, 12, 31),
        "requisiti": "Interventi su edifici esistenti. Certificazione medica che attesti la necessità dell'intervento. Conformità alla L. 13/1989 e al D.M. 236/1989. Spesa massima 96.000 euro.",
        "url_fonte": "https://www.agenziaentrate.gov.it/portale/barriere-architettoniche",
    },
]

VINCOLI = [
    {
        "id": "d0000001-0000-0000-0000-000000000001",
        "regione": "Lombardia",
        "provincia": "Milano",
        "comune": "Milano",
        "tipo_zona": "residenziale",
        "descrizione": "Zona residenziale di completamento. Indice di edificabilità territoriale: 2,5 mc/mq. Altezza massima: 12 metri. Distanza minima tra edifici: 10 metri. Distanza dalle strade: 5 metri.",
        "norma_riferimento": "Piano Regolatore Generale di Milano - NTA Art. 25",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000002",
        "regione": "Lombardia",
        "provincia": "Milano",
        "comune": "Milano",
        "tipo_zona": "agricola",
        "descrizione": "Zona agricola di tutela. E' vietata la costruzione di nuovi edifici. Ammessi solo interventi di manutenzione ordinaria e straordinaria su edifici esistenti. Indice di edificabilità: 0 mc/mq.",
        "norma_riferimento": "Piano Regolatore Generale di Milano - NTA Art. 38",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000003",
        "regione": "Lombardia",
        "provincia": "Milano",
        "comune": "Milano",
        "tipo_zona": "direzionale",
        "descrizione": "Zona direzionale e terziaria. Indice di edificabilità territoriale: 3,5 mc/mq. Altezza massima: 18 metri. Sono ammessi uffici, attività commerciali e servizi.",
        "norma_riferimento": "Piano Regolatore Generale di Milano - NTA Art. 30",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000004",
        "regione": "Lazio",
        "provincia": "Roma",
        "comune": "Roma",
        "tipo_zona": "storico",
        "descrizione": "Zona storica di centro antico. Vincolo paesaggistico e storico-artistico. Ogni intervento è soggetto ad autorizzazione della Soprintendenza. Ammessi solo interventi di restauro conservativo. Indice di edificabilità: 0 mc/mq per nuove costruzioni.",
        "norma_riferimento": "Piano Regolatore Generale di Roma - NTA Art. 12",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000005",
        "regione": "Lazio",
        "provincia": "Roma",
        "comune": "Roma",
        "tipo_zona": "residenziale",
        "descrizione": "Zona residenziale di tipo B. Indice di edificabilità territoriale: 1,5 mc/mq. Altezza massima: 10 metri. Distanza minima tra edifici: 8 metri. Sono ammessi interventi di nuova costruzione con Permesso di Costruire.",
        "norma_riferimento": "Piano Regolatore Generale di Roma - NTA Art. 22",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000006",
        "regione": "Toscana",
        "provincia": "Firenze",
        "comune": "Firenze",
        "tipo_zona": "storico",
        "descrizione": "Zona storica di centro antico. Vincolo paesaggistico e storico-artistico. Ammessi solo interventi di restauro conservativo e manutenzione. Vietata qualsiasi nuova costruzione. Tutti gli interventi sono soggetti a parere della Soprintendenza.",
        "norma_riferimento": "Piano Regolatore Generale di Firenze - NTA Art. 8",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000007",
        "regione": "Toscana",
        "provincia": "Firenze",
        "comune": "Firenze",
        "tipo_zona": "residenziale",
        "descrizione": "Zona residenziale di espansione. Indice di edificabilità territoriale: 2,0 mc/mq. Altezza massima: 11 metri. Distanza minima tra edifici: 8 metri. Sono ammessi interventi di nuova costruzione con Permesso di Costruire.",
        "norma_riferimento": "Piano Regolatore Generale di Firenze - NTA Art. 18",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000008",
        "regione": "Veneto",
        "provincia": "Venezia",
        "comune": "Venezia",
        "tipo_zona": "storico",
        "descrizione": "Zona storica di Venezia insulare. Vincolo paesaggistico, storico-artistico e idrogeologico. Ammessi solo interventi di restauro conservativo. Vietata qualsiasi nuova costruzione. Tutti gli interventi sono soggetti a parere della Soprintendenza e del Magistrato alle Acque.",
        "norma_riferimento": "Piano Regolatore Generale di Venezia - NTA Art. 5",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000009",
        "regione": "Veneto",
        "provincia": "Venezia",
        "comune": "Venezia",
        "tipo_zona": "industriale",
        "descrizione": "Zona industriale e artigianale di Marghera. Indice di edificabilità territoriale: 4,0 mc/mq. Altezza massima: 15 metri. Sono ammessi insediamenti produttivi, artigianali e commerciali. Permesso di Costruire obbligatorio.",
        "norma_riferimento": "Piano Regolatore Generale di Venezia - NTA Art. 35",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000010",
        "regione": "Campania",
        "provincia": "Napoli",
        "comune": "Napoli",
        "tipo_zona": "sismica",
        "descrizione": "Zona sismica di classe 2 (media sismicità). Tutti gli interventi di nuova costruzione e ristrutturazione sono soggetti alle norme sismiche della L. 64/1974 e delle NTC 2018. Obbligo di progetto strutturale e collaudo statico.",
        "norma_riferimento": "O.P.C.M. 3274/2003 - Classificazione sismica del territorio",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000011",
        "regione": "Sicilia",
        "provincia": "Catania",
        "comune": "Catania",
        "tipo_zona": "sismica",
        "descrizione": "Zona sismica di classe 2 (media sismicità). Tutti gli interventi di nuova costruzione e ristrutturazione sono soggetti alle norme sismiche della L. 64/1974 e delle NTC 2018. Obbligo di progetto strutturale e collaudo statico.",
        "norma_riferimento": "O.P.C.M. 3274/2003 - Classificazione sismica del territorio",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000012",
        "regione": "Emilia-Romagna",
        "provincia": "Bologna",
        "comune": "Bologna",
        "tipo_zona": "residenziale",
        "descrizione": "Zona residenziale di completamento. Indice di edificabilità territoriale: 2,0 mc/mq. Altezza massima: 10 metri. Distanza minima tra edifici: 8 metri. Distanza dalle strade: 5 metri. Permesso di Costruire per nuove costruzioni.",
        "norma_riferimento": "Piano Regolatore Generale di Bologna - NTA Art. 20",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000013",
        "regione": "Piemonte",
        "provincia": "Torino",
        "comune": "Torino",
        "tipo_zona": "residenziale",
        "descrizione": "Zona residenziale di tipo B. Indice di edificabilità territoriale: 1,8 mc/mq. Altezza massima: 12 metri. Distanza minima tra edifici: 8 metri. Ammessi interventi di nuova costruzione con Permesso di Costruire.",
        "norma_riferimento": "Piano Regolatore Generale di Torino - NTA Art. 24",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000014",
        "regione": "Piemonte",
        "provincia": "Torino",
        "comune": "Torino",
        "tipo_zona": "idrogeologica",
        "descrizione": "Vincolo idrogeologico. Area soggetta a rischio idraulico e frane. Permessi solo interventi di manutenzione ordinaria e straordinaria. Nuove costruzioni soggette a studio idrogeologico e parere dell'Autorità di Bacino.",
        "norma_riferimento": "Piano di Bacino del Fiume Po - Vincolo idrogeologico",
    },
    {
        "id": "d0000001-0000-0000-0000-000000000015",
        "regione": "Liguria",
        "provincia": "Genova",
        "comune": "Genova",
        "tipo_zona": "paesaggistica",
        "descrizione": "Vincolo paesaggistico. Area di particolare interesse paesaggistico e ambientale. Tutti gli interventi sono soggetti ad autorizzazione paesaggistica ai sensi del D.Lgs. 42/2004. Vietate le costruzioni che alterino il paesaggio.",
        "norma_riferimento": "D.Lgs. 42/2004 - Codice dei beni culturali e del paesaggio",
    },
]


# ============================================================================
# FUNZIONI DI INSERIMENTO
# ============================================================================

async def seed_database(database_url: str, embedding_provider: str = "local", embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    """Popola il database con dati reali italiani sull'edilizia."""
    from sqlalchemy import text as sql_text

    print("=" * 60)
    print("EdilEngine - Data Loader")
    print("=" * 60)
    print(f"Database: {database_url[:50]}...")
    print(f"Embedding provider: {embedding_provider}")
    print(f"Embedding model: {embedding_model}")
    print()

    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Ensure pgvector extension
        await conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async with async_session() as session:
        # ---- CATEGORIE ----
        print("📋 Inserimento categorie...")
        for cat_data in CATEGORIE:
            result = await session.execute(
                sql_text("SELECT id FROM categorie WHERE nome = :nome"),
                {"nome": cat_data["nome"]}
            )
            if result.scalar_one_or_none() is None:
                await session.execute(
                    sql_text(
                        "INSERT INTO categorie (id, nome) VALUES (:id, :nome) "
                        "ON CONFLICT (id) DO NOTHING"
                    ),
                    cat_data
                )
                print(f"  ✅ {cat_data['nome']}")
            else:
                print(f"  ⏭️  {cat_data['nome']} (già esistente)")

        # ---- LEGGI ----
        print("\n📋 Inserimento leggi...")
        for legge_data in LEGGI:
            categorie = legge_data.pop("categorie", [])
            result = await session.execute(
                sql_text("SELECT id FROM leggi WHERE url_fonte = :url"),
                {"url": legge_data["url_fonte"]}
            )
            if result.scalar_one_or_none() is None:
                await session.execute(
                    sql_text("""
                        INSERT INTO leggi (id, titolo, tipo, numero, data_emanazione, 
                        data_pubblicazione, data_vigore, autorita, testo_completo, url_fonte)
                        VALUES (:id, :titolo, :tipo, :numero, :data_emanazione, 
                        :data_pubblicazione, :data_vigore, :autorita, :testo_completo, :url_fonte)
                        ON CONFLICT (id) DO NOTHING
                    """),
                    legge_data
                )
                # Link categorie
                for cat_nome in categorie:
                    cat_result = await session.execute(
                        sql_text("SELECT id FROM categorie WHERE nome = :nome"),
                        {"nome": cat_nome}
                    )
                    cat_id = cat_result.scalar_one_or_none()
                    if cat_id:
                        await session.execute(
                            sql_text("""
                                INSERT INTO leggi_categorie (legge_id, categoria_id)
                                VALUES (:legge_id, :categoria_id)
                                ON CONFLICT DO NOTHING
                            """),
                            {"legge_id": legge_data["id"], "categoria_id": str(cat_id)}
                        )
                print(f"  ✅ {legge_data['titolo'][:60]}...")
            else:
                print(f"  ⏭️  {legge_data['titolo'][:60]}... (già esistente)")

        # ---- INCENTIVI ----
        print("\n📋 Inserimento incentivi...")
        for inc_data in INCENTIVI:
            result = await session.execute(
                sql_text("SELECT id FROM incentivi WHERE url_fonte = :url"),
                {"url": inc_data["url_fonte"]}
            )
            if result.scalar_one_or_none() is None:
                await session.execute(
                    sql_text("""
                        INSERT INTO incentivi (id, titolo, descrizione, ente_erogatore, tipo, 
                        aliquota, scadenza, requisiti, url_fonte)
                        VALUES (:id, :titolo, :descrizione, :ente_erogatore, :tipo, 
                        :aliquota, :scadenza, :requisiti, :url_fonte)
                        ON CONFLICT (id) DO NOTHING
                    """),
                    inc_data
                )
                print(f"  ✅ {inc_data['titolo']}")
            else:
                print(f"  ⏭️  {inc_data['titolo']} (già esistente)")

        # ---- VINCOLI ----
        print("\n📋 Inserimento vincoli...")
        for vin_data in VINCOLI:
            result = await session.execute(
                sql_text("SELECT id FROM vincoli WHERE id = :id"),
                {"id": vin_data["id"]}
            )
            if result.scalar_one_or_none() is None:
                await session.execute(
                    sql_text("""
                        INSERT INTO vincoli (id, regione, provincia, comune, tipo_zona, 
                        descrizione, norma_riferimento)
                        VALUES (:id, :regione, :provincia, :comune, :tipo_zona, 
                        :descrizione, :norma_riferimento)
                        ON CONFLICT (id) DO NOTHING
                    """),
                    vin_data
                )
                print(f"  ✅ {vin_data['comune']} - {vin_data['tipo_zona']}")
            else:
                print(f"  ⏭️  {vin_data['comune']} - {vin_data['tipo_zona']} (già esistente)")

        await session.commit()

    # ---- EMBEDDINGS ----
    print("\n📋 Generazione embeddings per le leggi...")
    print(f"   Provider: {embedding_provider}")
    print(f"   Modello: {embedding_model}")
    print("   (Questo può richiedere qualche minuto al primo avvio per il download del modello)")

    try:
        if embedding_provider.lower() == "local":
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(embedding_model)
            
            async with async_session() as session:
                # Get all laws without embeddings
                result = await session.execute(
                    sql_text("""
                        SELECT l.id, l.titolo, l.testo_completo
                        FROM leggi l
                        WHERE NOT EXISTS (
                            SELECT 1 FROM embedding_chunks ec WHERE ec.legge_id = l.id
                        )
                    """)
                )
                laws = result.mappings().all()

                if not laws:
                    print("  ⏭️  Tutte le leggi hanno già embeddings")
                else:
                    for law in laws:
                        text = law["testo_completo"] or law["titolo"]
                        # Split into chunks of ~500 characters
                        chunks = []
                        chunk_size = 500
                        overlap = 50
                        start = 0
                        while start < len(text):
                            end = start + chunk_size
                            chunk = text[start:end]
                            chunks.append(chunk)
                            start = end - overlap

                        # Generate embeddings
                        embeddings = model.encode(chunks, normalize_embeddings=True, batch_size=32)

                        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                            embedding_str = "[" + ",".join(str(x) for x in embedding.tolist()) + "]"
                            await session.execute(
                                sql_text("""
                                    INSERT INTO embedding_chunks (id, legge_id, chunk_text, chunk_index, embedding)
                                    VALUES (gen_random_uuid(), :legge_id, :chunk_text, :chunk_index, CAST(:embedding AS vector))
                                """),
                                {
                                    "legge_id": str(law["id"]),
                                    "chunk_text": chunk,
                                    "chunk_index": i,
                                    "embedding": embedding_str,
                                }
                            )
                        print(f"  ✅ {law['titolo'][:50]}... ({len(chunks)} chunks)")

                    await session.commit()
        else:
            print("  ⚠️  Provider OpenAI non ancora supportato nel seed script.")
            print("  Usa EMBEDDING_PROVIDER=local per generare gli embeddings.")

    except Exception as e:
        print(f"\n  ⚠️  Errore nella generazione degli embeddings: {e}")
        print("  I dati sono stati inseriti ma senza embeddings.")
        print("  Il semantic search non funzionerà finché non generi gli embeddings.")
        print("  Puoi ri-eseguire questo script per generare gli embeddings.")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("✅ Data loader completato!")
    print(f"   Categorie: {len(CATEGORIE)}")
    print(f"   Leggi: {len(LEGGI)}")
    print(f"   Incentivi: {len(INCENTIVI)}")
    print(f"   Vincoli: {len(VINCOLI)}")
    print("=" * 60)


if __name__ == "__main__":
    import os

    # Get database URL from environment or use default
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://edilengine:edilengine_dev@localhost:5432/edilengine"
    )

    # Convert sync URL to async if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    embedding_provider = os.environ.get("EMBEDDING_PROVIDER", "local")
    embedding_model = os.environ.get("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")

    asyncio.run(seed_database(database_url, embedding_provider, embedding_model))