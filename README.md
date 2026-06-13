# SENTRY-DVL

**Cascaded Hybrid Guardrail Architecture for LLM Fact-Verification**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20490643.svg)](https://doi.org/10.5281/zenodo.20490643)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

SENTRY-DVL prüft LLM-generierte Antworten gegen einen Referenzkontext
und blockiert abweichende, fehlerhafte oder widersprüchliche Ausgaben,
bevor sie dem Nutzer angezeigt werden.

Entwickelt für **High-Stakes-Systeme**: Medizin, Recht, Technik – überall wo
ein halluzinierter Wert echten Schaden anrichten kann.

> ⚠️ **Hinweis:** SENTRY-DVL ist ein Forschungsprototyp. Es ist nicht zertifiziert
> für den Einsatz in medizinischen, rechtlichen oder sicherheitskritischen
> Produktivsystemen. Nutzung auf eigene Verantwortung.

## Prinzip: Safety-First

```
FP-Rate = 0,0%  ←  nicht verhandelbar
FN akzeptiert   ←  lieber blockieren als falsch freigeben
```

## Installation

```bash
pip install sentry-dvl
```

Oder direkt aus dem Quellcode:

```bash
git clone https://github.com/joachim-ganter/sentry-dvl
cd sentry-dvl
pip install -e .
```

## Schnellstart

```python
from sentry_dvl import SentryDVL

sentry = SentryDVL()

kontext = "Die maximale Traglast beträgt 250 kN."
antwort = "Die Traglast beträgt maximal 280 kN."

verdict = sentry.evaluieren(kontext, antwort)
ausgabe = verdict.get_nutzer_antwort(antwort)

print(verdict.status)    # ABGELEHNT
print(verdict.konfidenz) # 0.0
print(ausgabe)           # Sicherheits-Fallback-Meldung
```

## Die drei Status-Werte

| Status | Bedeutung | Nutzer sieht |
|---|---|---|
| `FREIGEGEBEN` | Antwort ist verifiziert | Die Originalantwort |
| `UNSICHER` | Grenzbereich, nicht sicher genug | Verifikationshinweis |
| `ABGELEHNT` | Klare Abweichung erkannt | Sicherheits-Fallback |

## Architektur

```
Kontext + LLM-Antwort
        ↓
┌──────────────────────────────────────────────┐
│  1. ZahlenChecker     (deterministisch)      │
│  2. EinheitenChecker  (deterministisch)      │
│  3. NegationsChecker  (deterministisch)      │
│  4. SemantikChecker   (Embedding-Modell)     │
│  5. NLIChecker        (mDeBERTa, optional)   │
└──────────────────────────────────────────────┘
        ↓
  SentryVerdict
  .status / .konfidenz / .get_nutzer_antwort()
```

## EinheitenChecker (v1.2)

Erkennt medizinisch-kritische Faktor-1000-Fehler:

| Mutation | Beispiel | Risiko |
|---|---|---|
| mg → mcg/µg | 500 mg → 500 mcg | Unterdosierung |
| ml → µl | 2 ml → 2 µl | Unterdosierung |
| mmol → µmol | 5 mmol → 5 µmol | Messwertfehler |

## Benchmark (v1.2, 50 Testfälle, 7 Kategorien)

| Metrik | Wert |
|---|---|
| Präzision | 100,0% |
| FP-Rate | 0,0% |
| Kategorien | A–G |

## CLI

```bash
sentry-dvl check --kontext "Traglast 250 kN" --antwort "Traglast 280 kN"
sentry-dvl benchmark
sentry-dvl benchmark --kein-nli
sentry-dvl info
```

## Lizenz

SENTRY-DVL ist lizenziert unter **AGPL-3.0** für Forschung, Bildung und
Open-Source-Projekte.

**Kommerzielle Nutzung** erfordert eine separate Lizenz.
Anfragen an: **jo.ganter@googlemail.com**

## Zitation

```bibtex
@misc{ganter2025sentrydvl,
  author    = {Ganter, JoAchim},
  title     = {SENTRY-DVL: Cascaded Hybrid Guardrail Architecture
               for LLM Fact-Verification},
  year      = {2025},
  doi       = {10.5281/zenodo.20677551},
  publisher = {Zenodo}
}
```
