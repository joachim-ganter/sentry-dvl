"""Unit-Tests für die einzelnen Checker"""
import pytest
from sentry_dvl.checker import ZahlenChecker, EinheitenChecker, NegationsChecker


class TestZahlenChecker:
    def setup_method(self):
        self.checker = ZahlenChecker()

    def test_zahlen_erhalten(self):
        status, _, _ = self.checker.pruefen("Traglast 250 kN", "Die Traglast beträgt 250 kN.")
        assert status == "FREIGEGEBEN"

    def test_zahlenmutation(self):
        status, _, _ = self.checker.pruefen("Traglast 250 kN", "Die Traglast beträgt 280 kN.")
        assert status == "ABGELEHNT"

    def test_keine_zahlen(self):
        status, _, _ = self.checker.pruefen("Der Hund läuft.", "Der Hund rennt.")
        assert status == "FREIGEGEBEN"

    def test_zahlwort(self):
        status, _, _ = self.checker.pruefen("3 Parameter", "drei Parameter")
        assert status == "FREIGEGEBEN"

    def test_technischer_identifier(self):
        status, _, _ = self.checker.pruefen("AES-256", "AES-256-Verschlüsselung")
        assert status == "FREIGEGEBEN"


class TestEinheitenChecker:
    def setup_method(self):
        self.checker = EinheitenChecker()

    def test_mg_zu_mcg_mutation(self):
        status, _, _ = self.checker.pruefen(
            "Dosierung: 500 mg Wirkstoff täglich.",
            "Der Patient erhält 500 mcg Wirkstoff täglich."
        )
        assert status == "ABGELEHNT"

    def test_ml_zu_ul_mutation(self):
        status, _, _ = self.checker.pruefen(
            "Infusionslösung: 2 ml pro Stunde.",
            "Infusionsrate beträgt 2 µl pro Stunde."
        )
        assert status == "ABGELEHNT"

    def test_mg_erhalten(self):
        status, _, _ = self.checker.pruefen(
            "Das Produkt enthält 500 mg Wirkstoff.",
            "Jede Tablette enthält 500 mg des Wirkstoffs."
        )
        assert status == "FREIGEGEBEN"

    def test_keine_einheiten(self):
        status, _, _ = self.checker.pruefen(
            "Der Vertrag läuft bis 2025.",
            "Der Vertrag endet 2025."
        )
        assert status == "FREIGEGEBEN"

    def test_mmol_zu_umol_mutation(self):
        status, _, _ = self.checker.pruefen(
            "Serumkonzentration: 5 mmol/l.",
            "Der Messwert beträgt 5 µmol/l."
        )
        assert status == "ABGELEHNT"


class TestNegationsChecker:
    def setup_method(self):
        self.checker = NegationsChecker()

    def test_verbot_erhalten(self):
        status, _, _ = self.checker.pruefen(
            "Kinder dürfen das Medikament nicht einnehmen.",
            "Kinder dürfen das Medikament nicht einnehmen."
        )
        assert status == "FREIGEGEBEN"

    def test_verbot_verletzt(self):
        status, _, _ = self.checker.pruefen(
            "Kinder dürfen das Medikament nicht einnehmen.",
            "Kinder können das Medikament einnehmen."
        )
        assert status == "ABGELEHNT"

    def test_schwache_negation_ignoriert(self):
        status, _, _ = self.checker.pruefen(
            "Nicht nur Erwachsene profitieren.",
            "Alle Altersgruppen profitieren."
        )
        assert status == "FREIGEGEBEN"

    def test_semantisches_aequivalent(self):
        status, _, _ = self.checker.pruefen(
            "Kein Zutritt ohne Schutzausrüstung.",
            "Schutzausrüstung ist zwingend erforderlich."
        )
        assert status == "FREIGEGEBEN"
