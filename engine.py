"""SENTRY-DVL Engine – Haupt-Orchestrierung"""
import logging

from verdict import SentryVerdict
from checker import ZahlenChecker, EinheitenChecker, NegationsChecker, SemantikChecker, NLIChecker

log = logging.getLogger("SENTRY-DVL")


class SentryDVL:
    EMBEDDING_MODELL = "paraphrase-multilingual-mpnet-base-v2"

    def __init__(self, mit_nli: bool = True, verbose: bool = True):
        if verbose:
            print("Initialisiere SENTRY-DVL v1.2...\n")

        from sentence_transformers import SentenceTransformer
        if verbose:
            print(f"  Lade Embedding-Modell ({self.EMBEDDING_MODELL})...")
        embedding = SentenceTransformer(self.EMBEDDING_MODELL)

        self._checker = [
            ("Zahlen",    ZahlenChecker()),
            ("Einheiten", EinheitenChecker()),
            ("Negation",  NegationsChecker()),
            ("Semantik",  SemantikChecker(embedding)),
        ]
        if mit_nli:
            self._checker.append(("NLI", NLIChecker()))

        if verbose:
            print("\nSENTRY-DVL v1.2 bereit.")
            print("  Modus   : SAFETY-FIRST")
            print("  Status  : FREIGEGEBEN | UNSICHER | ABGELEHNT")
            print("  Ziel    : FP-Rate = 0,0%\n")

    def evaluieren(self, kontext: str, antwort: str) -> SentryVerdict:
        if antwort.strip() == kontext.strip() or len(antwort.strip()) < 8:
            return SentryVerdict(
                status="FREIGEGEBEN", ist_sicher=True, konfidenz=1.0,
                begruendung="Identisch oder Kurztext",
                nutzer_msg=None, checker="Kurzschluss"
            )

        freigegeben_konfidenzen = []

        for name, checker in self._checker:
            status, konfidenz, begruendung = checker.pruefen(kontext, antwort)

            if status == "ABGELEHNT":
                log.warning(f"ABGELEHNT von {name}: {begruendung}")
                return SentryVerdict(
                    status="ABGELEHNT", ist_sicher=False,
                    konfidenz=konfidenz, begruendung=begruendung,
                    nutzer_msg=SentryVerdict.MELDUNGEN["ABGELEHNT"],
                    checker=name
                )
            if status == "UNSICHER":
                log.warning(f"UNSICHER von {name}: {begruendung}")
                return SentryVerdict(
                    status="UNSICHER", ist_sicher=False,
                    konfidenz=konfidenz, begruendung=begruendung,
                    nutzer_msg=SentryVerdict.MELDUNGEN["UNSICHER"],
                    checker=name
                )

            freigegeben_konfidenzen.append(konfidenz)

        gesamt_konfidenz = round(min(freigegeben_konfidenzen), 3)
        return SentryVerdict(
            status="FREIGEGEBEN", ist_sicher=True,
            konfidenz=gesamt_konfidenz,
            begruendung="Alle Prüfungen bestanden",
            nutzer_msg=None, checker="ALLE"
        )
