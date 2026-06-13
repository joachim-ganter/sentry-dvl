"""
SENTRY-DVL – Die fünf Prüf-Schichten

Reihenfolge nach Kosten (günstigste zuerst):
    1. ZahlenChecker     – O(n), kein Modell, deterministisch
    2. EinheitenChecker  – O(n), kein Modell, deterministisch
    3. NegationsChecker  – O(n), kein Modell, deterministisch
    4. SemantikChecker   – Embedding-Modell (bereits geladen)
    5. NLIChecker        – mDeBERTa, nur wenn 1–4 bestehen
"""
import re
import logging
from typing import Tuple

import numpy as np
import torch
import torch.nn.functional as F

log = logging.getLogger("SENTRY-DVL")

# Typ-Alias für Checker-Rückgabe
CheckResult = Tuple[str, float, str]  # (status, konfidenz, begruendung)


class ZahlenChecker:
    """
    Schicht 1: Zahlen-Integritätsprüfung.

    Erkennt Zahlenmutationen (250 kN → 280 kN) und Vagheit
    die präzise Werte ersetzt (99,9 % → "nahezu immer").

    Lookbehind/Lookahead schließt Ziffern und Buchstaben aus:
    AES-256 → "256" wird nicht extrahiert.
    m²      → "2" wird nicht extrahiert.
    """

    MUSTER = re.compile(r'(?<![A-Za-z0-9\-])(\d+[.,]?\d*)(?![A-Za-z0-9])')

    ZAHLWORT_MAP = {
        # Deutsch
        "null": "0",  "ein": "1",    "eine": "1",   "einen": "1",
        "zwei": "2",  "drei": "3",   "vier": "4",   "fünf": "5",
        "sechs": "6", "sieben": "7", "acht": "8",   "neun": "9",
        "zehn": "10", "elf": "11",   "zwölf": "12", "zwanzig": "20",
        "dreißig": "30", "hundert": "100", "tausend": "1000",
        # Englisch
        "zero": "0",  "one": "1",    "two": "2",    "three": "3",
        "four": "4",  "five": "5",   "six": "6",    "seven": "7",
        "eight": "8", "nine": "9",   "ten": "10",   "eleven": "11",
        "twelve": "12", "twenty": "20", "hundred": "100", "thousand": "1000",
    }
    ZAHLWORT_MUSTER = re.compile(
        r'\b(' + '|'.join(ZAHLWORT_MAP.keys()) + r')\b', re.IGNORECASE
    )

    def _extrahieren(self, text: str) -> set:
        zahlen = {n.replace(',', '.') for n in self.MUSTER.findall(text)}
        for m in self.ZAHLWORT_MUSTER.finditer(text):
            zahlen.add(self.ZAHLWORT_MAP[m.group(1).lower()])
        return zahlen

    def pruefen(self, kontext: str, antwort: str) -> CheckResult:
        kont = self._extrahieren(kontext)
        antw = self._extrahieren(antwort)
        if not kont:
            return "FREIGEGEBEN", 1.0, "Keine Zahlen im Kontext"
        fehlend = kont - antw
        if fehlend:
            return "ABGELEHNT", 0.0, f"Zahlen fehlen oder mutiert: {fehlend}"
        return "FREIGEGEBEN", 1.0, "Alle Zahlen erhalten"


class EinheitenChecker:
    """
    Schicht 2: Medizinisch-kritische Einheitenmutationsprüfung.

    Erkennt Faktor-1000-Fehler bei Einheiten die in der Praxis
    lebensbedrohlich sind (mg vs. mcg/µg, ml vs. µl, mmol vs. µmol).

    Strategie:
        - Extrahiere alle (Zahl, Einheit)-Paare aus Kontext und Antwort
        - Prüfe ob eine Einheit durch eine verwechselbare ersetzt wurde
        - Prüfe ob der numerische Wert als Kompensation angepasst wurde

    Beispiele die ABGELEHNT werden:
        "500 mg"  → "0,5 g"    (Faktor-1000, andere Einheit)
        "500 mg"  → "500 mcg"  (Einheitenmutation, gleicher Wert)
        "2 ml"    → "2 µl"     (Faktor-1000, gleicher Wert)
    """

    # Einheiten-Gruppen: verwechselbare Paare mit Umrechnungsfaktor
    VERWECHSLUNGS_PAARE = [
        # (einheit_a, einheit_b, faktor_a_zu_b)
        # mg ↔ mcg/µg  (1 mg = 1000 mcg)
        (r'mg',   r'mcg|µg|microg',  1000),
        # g ↔ mg       (1 g = 1000 mg)
        (r'\bg\b', r'mg',            1000),
        # ml ↔ µl      (1 ml = 1000 µl)
        (r'ml',   r'µl|microl',      1000),
        # l ↔ ml       (1 l = 1000 ml)
        (r'\bl\b', r'ml',            1000),
        # mmol ↔ µmol  (1 mmol = 1000 µmol)
        (r'mmol', r'µmol|micromol',  1000),
        # mol ↔ mmol   (1 mol = 1000 mmol)
        (r'\bmol\b', r'mmol',        1000),
    ]

    # Extrahiert (wert, einheit)-Paare
    EINHEIT_MUSTER = re.compile(
        r'(\d+[.,]?\d*)\s*(mg|mcg|µg|microg|'
        r'\bg\b|ml|µl|microl|\bl\b|mmol|µmol|micromol|\bmol\b)',
        re.IGNORECASE
    )

    def _extrahieren(self, text: str):
        """Gibt Liste von (float_wert, einheit_lower) zurück."""
        paare = []
        for m in self.EINHEIT_MUSTER.finditer(text):
            wert = float(m.group(1).replace(',', '.'))
            einheit = m.group(2).lower()
            paare.append((wert, einheit))
        return paare

    def _normalisiere_einheit(self, einheit: str) -> str:
        """Vereinheitlicht Schreibweisen (µg, mcg, microg → mcg)."""
        e = einheit.lower()
        if e in ('µg', 'microg'):
            return 'mcg'
        if e in ('µl', 'microl'):
            return 'µl'
        if e in ('µmol', 'micromol'):
            return 'µmol'
        return e

    def pruefen(self, kontext: str, antwort: str) -> CheckResult:
        kont_paare = self._extrahieren(kontext)
        antw_paare = self._extrahieren(antwort)

        if not kont_paare:
            return "FREIGEGEBEN", 1.0, "Keine kritischen Einheiten im Kontext"

        # Für jedes Kontext-Paar: prüfe ob eine gefährliche Mutation vorliegt
        for k_wert, k_einheit in kont_paare:
            k_norm = self._normalisiere_einheit(k_einheit)

            for a_wert, a_einheit in antw_paare:
                a_norm = self._normalisiere_einheit(a_einheit)

                if k_norm == a_norm:
                    continue  # gleiche Einheit, ZahlenChecker übernimmt

                # Prüfe ob dieses Paar ein Verwechslungs-Paar ist
                for einheit_a, einheit_b_muster, faktor in self.VERWECHSLUNGS_PAARE:
                    a_passt = bool(re.fullmatch(einheit_a, k_norm, re.IGNORECASE))
                    b_passt = bool(re.search(einheit_b_muster, a_norm, re.IGNORECASE))

                    if a_passt and b_passt:
                        # Einheitenmutation erkannt — Wert egal
                        return (
                            "ABGELEHNT", 0.0,
                            f"Einheitenmutation: {k_wert} {k_einheit} → "
                            f"{a_wert} {a_einheit} "
                            f"(Faktor-{faktor}-Fehler möglich)"
                        )

        return "FREIGEGEBEN", 1.0, "Keine kritischen Einheitenmutationen"


class NegationsChecker:
    """
    Schicht 3: Verbots-Umkehrungsprüfung.

    Unterscheidet harte Verbote ("darf nicht", "verboten")
    von schwachen Negationen ("nicht nur", "nicht schwer").

    Semantische Äquivalente ("zwingend", "untersagt") ersetzen
    explizite Verneinung und gelten als erhaltenes Verbot.
    """

    HART = re.compile(
        r'\b(darf\s+nicht|dürfen\s+nicht|muss\s+nicht|kein\s+Zutritt|'
        r'nicht\s+erlaubt|nicht\s+zugelassen|nicht\s+gestattet|'
        r'verboten|untersagt|ausgeschlossen|'
        r'nur\s+nach\s+\w+\s+Genehmigung|nur\s+für\s+autorisiert|'
        r'must\s+not|may\s+not|shall\s+not|not\s+allowed|not\s+permitted|'
        r'forbidden|prohibited|banned)\b',
        re.IGNORECASE
    )
    AEQUIVALENT = re.compile(
        r'\b(verboten|untersagt|ausgeschlossen|zwingend|verpflichtend|'
        r'erforderlich|ausschließlich|nicht\s+erlaubt|nicht\s+gestattet|'
        r'nicht\s+zugelassen|nur\s+für|nur\s+mit|nur\s+nach|nur\s+durch|'
        r'unbefugt|gesperrt|mandatory|required|compulsory|unauthorized|'
        r'restricted|forbidden|prohibited)\b',
        re.IGNORECASE
    )

    def pruefen(self, kontext: str, antwort: str) -> CheckResult:
        if not self.HART.search(kontext):
            return "FREIGEGEBEN", 1.0, "Kein hartes Verbot im Kontext"
        if not self.HART.search(antwort) and not self.AEQUIVALENT.search(antwort):
            return "ABGELEHNT", 0.0, "Hartes Verbot aus Antwort entfernt"
        return "FREIGEGEBEN", 1.0, "Verbot semantisch erhalten"


class SemantikChecker:
    """
    Schicht 4: Kosinus-Ähnlichkeit mit 3-Zonen-Bewertung.

        sim >= SCHWELLE_SICHER  → FREIGEGEBEN
        sim >= SCHWELLE_GEWISS  → UNSICHER (Grenzbereich)
        sim <  SCHWELLE_GEWISS  → ABGELEHNT
    """

    SCHWELLE_SICHER = 0.70
    SCHWELLE_GEWISS = 0.64

    def __init__(self, modell):
        self.modell = modell

    def pruefen(self, kontext: str, antwort: str) -> CheckResult:
        v1  = self.modell.encode(kontext, normalize_embeddings=True)
        v2  = self.modell.encode(antwort, normalize_embeddings=True)
        sim = float(np.dot(v1, v2))

        if sim >= self.SCHWELLE_SICHER:
            return "FREIGEGEBEN", round(sim, 3), f"Semantisch konsistent (sim={sim:.3f})"
        if sim >= self.SCHWELLE_GEWISS:
            return "UNSICHER", round(sim, 3), \
                f"Grenzbereich (sim={sim:.3f}, Schwelle={self.SCHWELLE_SICHER})"
        return "ABGELEHNT", round(1.0 - sim, 3), f"Semantische Distanz (sim={sim:.3f})"


class NLIChecker:
    """
    Schicht 5: Natural Language Inference – Widerspruchserkennung.

    Modell: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli (mehrsprachig)

        widerspruch >= WIDERSPRUCH_HART     → ABGELEHNT
        widerspruch >= WIDERSPRUCH_VERDACHT → UNSICHER
        widerspruch <  WIDERSPRUCH_VERDACHT → FREIGEGEBEN

    Konfidenz-Untergrenze (KONFIDENZ_BODEN) verhindert irreführend
    niedrige Gesamt-Konfidenz bei inhaltlich korrekten Antworten.
    """

    MODELL_NAME          = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    WIDERSPRUCH_HART     = 0.55
    WIDERSPRUCH_VERDACHT = 0.30
    KONFIDENZ_BODEN      = 0.40

    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        log.info(f"Lade NLI-Modell: {self.MODELL_NAME}")
        self.tok      = AutoTokenizer.from_pretrained(self.MODELL_NAME)
        self.mdl      = AutoModelForSequenceClassification.from_pretrained(self.MODELL_NAME)
        self.mdl.eval()
        self.id2label = self.mdl.config.id2label

    def _wahrscheinlichkeiten(self, kont: str, antw: str):
        inp = self.tok(kont, antw, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = self.mdl(**inp).logits
        return F.softmax(logits, dim=-1)[0]

    def _index(self, schluessel: str):
        for i, lbl in self.id2label.items():
            if schluessel in lbl.lower():
                return int(i)
        return None

    def pruefen(self, kontext: str, antwort: str) -> CheckResult:
        probs = self._wahrscheinlichkeiten(kontext, antwort)
        wi    = self._index("contra")
        ei    = self._index("entail")
        ws    = probs[wi].item() if wi is not None else 0.0
        es    = probs[ei].item() if ei is not None else 0.0

        if ws >= self.WIDERSPRUCH_HART:
            return "ABGELEHNT", round(ws, 3), \
                f"NLI Widerspruch bestätigt (widerspruch={ws:.2f})"
        if ws >= self.WIDERSPRUCH_VERDACHT:
            return "UNSICHER", round(ws, 3), \
                f"NLI Widerspruch vermutet (widerspruch={ws:.2f}, übereinstimmung={es:.2f})"

        konfidenz = max(round(es, 3), self.KONFIDENZ_BODEN)
        return "FREIGEGEBEN", konfidenz, \
            f"NLI unauffällig (widerspruch={ws:.2f}, übereinstimmung={es:.2f})"
