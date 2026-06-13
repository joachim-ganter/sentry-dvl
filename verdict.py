"""SentryVerdict – Ausgabe-Datenstruktur"""
from dataclasses import dataclass


@dataclass
class SentryVerdict:
    status:      str
    ist_sicher:  bool
    konfidenz:   float
    begruendung: str
    nutzer_msg:  str
    checker:     str

    MELDUNGEN = {
        "FREIGEGEBEN": None,
        "UNSICHER": (
            "Diese Antwort konnte nicht vollständig gegen den Quellkontext "
            "verifiziert werden. Bitte prüfen Sie das Originaldokument."
        ),
        "ABGELEHNT": (
            "Die generierte Antwort weicht vom Referenzkontext ab. "
            "Aus Sicherheitsgründen wird sie nicht angezeigt."
        ),
    }

    def get_nutzer_antwort(self, rohausgabe: str) -> str:
        if self.status == "FREIGEGEBEN":
            return rohausgabe
        return self.MELDUNGEN[self.status]

    def __str__(self) -> str:
        return (
            f"[{self.status}] konfidenz={self.konfidenz:.2f} "
            f"checker={self.checker} | {self.begruendung}"
        )
