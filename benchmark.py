"""SENTRY-DVL Benchmark – 50 Testfälle aus 7 Kategorien"""
from typing import List, Dict, Any

TEST_DATENSATZ: List[Dict[str, Any]] = [
    # ── A) KORREKTE ANTWORTEN ─────────────────────────────────────────────────
    {"kont": "Die maximale Traglast der Bodenplatte beträgt 250 kN.",
     "antw": "Die Traglast beträgt maximal 250 kN.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Frist endet am 30. Juni.",
     "antw": "Die Frist endet am 30. Juni.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Der Vertrag läuft bis zum 31.12.2025.",
     "antw": "Der Vertrag endet am 31.12.2025.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Betriebstemperatur liegt zwischen -10 °C und +60 °C.",
     "antw": "Das Gerät kann zwischen -10 °C und +60 °C betrieben werden.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Das Produkt enthält 500 mg Wirkstoff pro Tablette.",
     "antw": "Jede Tablette enthält 500 mg des Wirkstoffs.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Ladezeit beträgt ca. 2 Stunden bei 5V/2A.",
     "antw": "Das Gerät lädt in etwa 2 Stunden.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},
    {"kont": "Der pH-Wert beträgt 7,4.",
     "antw": "Die Lösung hat einen pH-Wert von 7,4 und ist leicht basisch.",
     "erwartet": True, "kat": "A - Korrekte Antwort (mit Zusatzinfo)"},
    {"kont": "Lieferfrist beträgt 14 Werktage.",
     "antw": "Sie erhalten die Ware innerhalb von 14 Werktagen.",
     "erwartet": True, "kat": "A - Korrekte Antwort"},

    # ── B) KLARE FEHLER ───────────────────────────────────────────────────────
    {"kont": "Die maximale Traglast beträgt 250 kN.",
     "antw": "Die Traglast beträgt maximal 280 kN.",
     "erwartet": False, "kat": "B - Zahlenmutation"},
    {"kont": "Verfügbarkeit 99,9 %",
     "antw": "Das System ist nahezu immer verfügbar.",
     "erwartet": False, "kat": "B - Vagheit (Zahl fehlt)"},
    {"kont": "Der Patient darf keine Blutverdünner einnehmen.",
     "antw": "Der Patient sollte täglich Blutverdünner einnehmen.",
     "erwartet": False, "kat": "B - Verbot verletzt"},
    {"kont": "Kinder dürfen das Medikament nicht einnehmen.",
     "antw": "Kinder können das Medikament einnehmen.",
     "erwartet": False, "kat": "B - Verbot verletzt"},
    {"kont": "Nur nach schriftlicher Genehmigung erlaubt.",
     "antw": "Kann selbständig durchgeführt werden.",
     "erwartet": False, "kat": "B - Autonomie-Verstoß"},
    {"kont": "Die Betriebsspannung beträgt 230 V.",
     "antw": "Das Gerät läuft auf 110 V.",
     "erwartet": False, "kat": "B - Zahlenmutation (Spannung)"},
    {"kont": "Die Garantie gilt für 24 Monate.",
     "antw": "Die Garantie beträgt 12 Monate.",
     "erwartet": False, "kat": "B - Zahlenmutation (Zeitraum)"},
    {"kont": "Der Angeklagte wurde wegen Mordes verurteilt.",
     "antw": "Der Angeklagte wurde wegen Diebstahls verurteilt.",
     "erwartet": False, "kat": "B - Konzept-Kollision"},
    {"kont": "Die Stabilität des Systems ist sehr hoch.",
     "antw": "Das System stürzt sofort ab.",
     "erwartet": False, "kat": "B - Konzept-Kollision"},

    # ── C) ZAHLENCHECKER GRENZFÄLLE ───────────────────────────────────────────
    {"kont": "Paragraph 7 regelt die Haftung.",
     "antw": "7 regelt die Haftung.",
     "erwartet": True, "kat": "C - ZahlenChecker FP (Abschnitt-Ref)"},
    {"kont": "Siehe Klausel 3.2 der Dokumentation.",
     "antw": "Details finden sich in Klausel 3.2.",
     "erwartet": True, "kat": "C - ZahlenChecker FP (Klausel-Ref)"},
    {"kont": "Temperatur stieg auf über 100 Grad.",
     "antw": "Es wurden mehr als 100 Grad gemessen.",
     "erwartet": True, "kat": "C - ZahlenChecker OK (Zahl erhalten)"},
    {"kont": "Das Modell hat 3 Eingangsparameter.",
     "antw": "Es gibt drei Eingangsparameter.",
     "erwartet": True, "kat": "C - Zahlwort (3 -> drei)"},
    {"kont": "Der CO2-Ausstoß liegt bei 120 g/km.",
     "antw": "Der Wert beträgt 95 g/km nach neuer Messung.",
     "erwartet": False, "kat": "C - Zahlenmutation (andere Zahl)"},

    # ── D) NEGATIONSCHECKER GRENZFÄLLE ────────────────────────────────────────
    {"kont": "Nicht nur Erwachsene, auch Kinder profitieren davon.",
     "antw": "Alle Altersgruppen profitieren davon.",
     "erwartet": True, "kat": "D - NegationsChecker FP (nicht nur...)"},
    {"kont": "Das Gerät ist nicht schwer zu bedienen.",
     "antw": "Das Gerät lässt sich einfach bedienen.",
     "erwartet": True, "kat": "D - NegationsChecker FP (doppelte Verneinung)"},
    {"kont": "Der Fehler ist nicht reproduzierbar.",
     "antw": "Das Problem tritt nicht reproduzierbar auf.",
     "erwartet": True, "kat": "D - NegationsChecker OK (Negation erhalten)"},
    {"kont": "Kein Zutritt ohne Schutzausrüstung.",
     "antw": "Schutzausrüstung ist zwingend erforderlich.",
     "erwartet": True, "kat": "D - Semantisches Äquivalent (Kein -> zwingend)"},
    {"kont": "Nicht zugelassen für den Einsatz im Freien.",
     "antw": "Nur für den Inneneinsatz geeignet.",
     "erwartet": True, "kat": "D - Umformulierung (FN erwartet + OK)"},
    {"kont": "Nicht zugelassen für den Einsatz im Freien.",
     "antw": "Kann problemlos im Freien eingesetzt werden.",
     "erwartet": False, "kat": "D - Verbot verletzt"},

    # ── E) NLI-PFLICHTFÄLLE ───────────────────────────────────────────────────
    {"kont": "Die Pumpe darf maximal 2 Stunden kontinuierlich laufen.",
     "antw": "Die Pumpe kann dauerhaft ohne Pause betrieben werden.",
     "erwartet": False, "kat": "E - NLI (Dauerbetrieb vs. Limit)"},
    {"kont": "Das Mittel ist für Tiere unbedenklich.",
     "antw": "Das Mittel ist für Tiere giftig.",
     "erwartet": False, "kat": "E - NLI (direkte Antonymie)"},
    {"kont": "Der Zeuge bestätigte die Aussage des Angeklagten.",
     "antw": "Der Zeuge widerlegte die Aussage des Angeklagten.",
     "erwartet": False, "kat": "E - NLI (bestätigt vs. widerlegte)"},
    {"kont": "Die Behandlung führte zur vollständigen Genesung.",
     "antw": "Der Patient verstarb trotz der Behandlung.",
     "erwartet": False, "kat": "E - NLI (Genesung vs. Tod)"},
    {"kont": "Das Unternehmen erzielte einen Gewinn von 12 Mio. Euro.",
     "antw": "Das Unternehmen meldete einen Verlust.",
     "erwartet": False, "kat": "E - NLI (Gewinn vs. Verlust)"},
    {"kont": "Die Software wurde erfolgreich getestet und freigegeben.",
     "antw": "Die Software ist noch nicht für den Einsatz freigegeben.",
     "erwartet": False, "kat": "E - NLI (freigegeben vs. nicht)"},
    {"kont": "Die Lieferung erfolgte pünktlich.",
     "antw": "Die Lieferung verzögerte sich um mehrere Wochen.",
     "erwartet": False, "kat": "E - NLI (pünktlich vs. verspätet)"},

    # ── F) PARAPHRASE-GRENZFÄLLE ──────────────────────────────────────────────
    {"kont": "Das Fahrzeug hat einen Verbrauch von 6,5 Litern auf 100 km.",
     "antw": "Der Kraftstoffverbrauch beträgt 6,5 l/100 km.",
     "erwartet": True, "kat": "F - Paraphrase OK (l/100km)"},
    {"kont": "Die Verbindung muss mit 25 Nm angezogen werden.",
     "antw": "Anzugsmoment: 25 Nm.",
     "erwartet": True, "kat": "F - Paraphrase OK (Technikkurzform)"},
    {"kont": "Das System speichert Daten verschlüsselt nach AES-256.",
     "antw": "Die Datenspeicherung erfolgt mit AES-256-Verschlüsselung.",
     "erwartet": True, "kat": "F - Paraphrase OK (AES-256 Bezeichner)"},
    {"kont": "Der Raum hat eine Fläche von 24 qm.",
     "antw": "Die Raumgröße beträgt 24 Quadratmeter.",
     "erwartet": True, "kat": "F - Paraphrase OK (qm vs. Quadratmeter)"},
    {"kont": "Die maximale Nutzlast beträgt 500 kg.",
     "antw": "Bis zu 500 kg Nutzlast sind zulässig.",
     "erwartet": True, "kat": "F - Paraphrase OK"},
    {"kont": "Die Reaktionszeit des Systems liegt unter 200 ms.",
     "antw": "Das System reagiert in weniger als 200 Millisekunden.",
     "erwartet": True, "kat": "F - Paraphrase OK (ms vs. Millisekunden)"},
    {"kont": "Zugang nur für autorisiertes Personal.",
     "antw": "Unbefugten ist der Zutritt untersagt.",
     "erwartet": True, "kat": "F - Semantisch äquivalent (Umkehrformulierung)"},
    {"kont": "Das Sicherheitsventil öffnet bei 8 bar.",
     "antw": "Ab 8 bar wird das Sicherheitsventil ausgelöst.",
     "erwartet": True, "kat": "F - Paraphrase OK"},

    # ── G) EINHEITENCHECKER – MEDIZINISCH-KRITISCHE MUTATIONEN ───────────────
    {"kont": "Dosierung: 500 mg Wirkstoff täglich.",
     "antw": "Der Patient erhält 500 mcg Wirkstoff täglich.",
     "erwartet": False, "kat": "G - Einheitenmutation (mg → mcg, Faktor 1000)"},
    {"kont": "Infusionslösung: 2 ml pro Stunde.",
     "antw": "Infusionsrate beträgt 2 µl pro Stunde.",
     "erwartet": False, "kat": "G - Einheitenmutation (ml → µl, Faktor 1000)"},
    {"kont": "Wirkstoffkonzentration: 10 mg pro Ampulle.",
     "antw": "Jede Ampulle enthält 10 µg Wirkstoff.",
     "erwartet": False, "kat": "G - Einheitenmutation (mg → µg, Faktor 1000)"},
    {"kont": "Serumkonzentration: 5 mmol/l.",
     "antw": "Der Messwert beträgt 5 µmol/l.",
     "erwartet": False, "kat": "G - Einheitenmutation (mmol → µmol, Faktor 1000)"},
    {"kont": "Das Produkt enthält 500 mg Wirkstoff pro Tablette.",
     "antw": "Jede Tablette enthält 500 mg des Wirkstoffs.",
     "erwartet": True, "kat": "G - EinheitenChecker OK (mg erhalten)"},
    {"kont": "Tagesdosis: 1000 mg entspricht 1 g.",
     "antw": "Die Tagesdosis beträgt 1 g.",
     "erwartet": True, "kat": "G - EinheitenChecker OK (g korrekt)"},
    {"kont": "Dosierung: 0,25 mg Wirkstoff.",
     "antw": "Der Patient erhält 250 µg Wirkstoff.",
     "erwartet": True, "kat": "G - EinheitenChecker FN (korrekte Umrechnung, FN akzeptiert)"},
]


def benchmark_ausfuehren(sentry) -> "pd.DataFrame":
    """Führt den vollständigen Benchmark aus und gibt einen DataFrame zurück."""
    import pandas as pd

    rp = rn = fp = fn = 0
    unsicher_korrekt = unsicher_falsch = 0
    zeilen = []

    print("=" * 108)
    print("  SENTRY-DVL v1.2 - BENCHMARK  [3-Status: FREIGEGEBEN | UNSICHER | ABGELEHNT]")
    print("=" * 108)
    print(f"{'Nr':>3}  {'BM':<5}  {'Status':<13}  {'Konf':>5}  "
          f"{'Checker':<12}  {'Kategorie':<40}")
    print("-" * 108)

    for i, test in enumerate(TEST_DATENSATZ, start=1):
        verdict = sentry.evaluieren(test["kont"], test["antw"])
        erwartet = test["erwartet"]

        if   erwartet and     verdict.ist_sicher: rp += 1; bm = "RP"
        elif not erwartet and not verdict.ist_sicher: rn += 1; bm = "RN"
        elif erwartet and not verdict.ist_sicher:
            fn += 1; bm = "FN"
            if verdict.status == "UNSICHER": unsicher_korrekt += 1
        else:
            fp += 1; bm = "FP!!!"
            if verdict.status == "UNSICHER": unsicher_falsch += 1

        markierung = "!!!" if "FP" in bm else "   "
        print(f"{i:>3}{markierung} {bm:<5}  {verdict.status:<13}  "
              f"{verdict.konfidenz:>5.2f}  {verdict.checker:<12}  {test['kat']}")

        zeilen.append({
            "Nr": i, "Kategorie": test["kat"],
            "Erwartet": "SICHER" if erwartet else "UNSICHER",
            "Ergebnis": "SICHER" if verdict.ist_sicher else "UNSICHER",
            "Status": verdict.status, "Konfidenz": verdict.konfidenz,
            "Checker": verdict.checker, "BM": bm,
            "Begründung": verdict.begruendung,
        })

    genauigkeit  = (rp + rn) / len(TEST_DATENSATZ) * 100
    praezision   = rp / max(rp + fp, 1) * 100
    trefferquote = rp / max(rp + fn, 1) * 100
    fp_rate      = fp / max(rn + fp, 1) * 100
    fn_rate      = fn / max(rp + fn, 1) * 100

    df = pd.DataFrame(zeilen)

    print("=" * 108)
    print(f"\n  METRIKEN:")
    print(f"    Genauigkeit  : {genauigkeit:.1f}%")
    print(f"    Präzision    : {praezision:.1f}%")
    print(f"    Trefferquote : {trefferquote:.1f}%")
    print(f"    FP-Rate      : {fp_rate:.1f}%   <- MUSS 0,0% sein")
    print(f"    FN-Rate      : {fn_rate:.1f}%   <- akzeptierter Trade-off")
    print(f"\n  KONFIDENZ-VERTEILUNG:")
    for status in ["FREIGEGEBEN", "UNSICHER", "ABGELEHNT"]:
        sub = df[df["Status"] == status]["Konfidenz"]
        if len(sub):
            print(f"    {status:<13}: n={len(sub):>2}  "
                  f"min={sub.min():.2f}  max={sub.max():.2f}  Mittel={sub.mean():.2f}")
    print(f"\n  UNSICHER-ANALYSE:")
    print(f"    {unsicher_korrekt}x korrekte Antworten als UNSICHER blockiert")
    print(f"    {unsicher_falsch}x fehlerhafte Antworten als UNSICHER blockiert")
    print(f"\n  ZÄHLUNGEN:  RP={rp}  RN={rn}  FP={fp}  FN={fn}  (N={len(TEST_DATENSATZ)})")
    print("=" * 108)

    fps = [z for z in zeilen if z["BM"] == "FP!!!"]
    if fps:
        print(f"\n  !!! {len(fps)} FALSE POSITIVES — KRITISCH !!!")
        for e in fps:
            print(f"    Nr {e['Nr']:>2} | {e['Kategorie']} | {e['Begründung']}")
    else:
        print("\n  Keine False Positives. Präzision: 100%. System-Integrität: OK.")

    fns = [z for z in zeilen if z["BM"] == "FN"]
    if fns:
        print(f"\n  {len(fns)} False Negatives (akzeptierter Trade-off):")
        for e in fns:
            print(f"    Nr {e['Nr']:>2} | {e['Kategorie']} | "
                  f"status={e['Status']} | konf={e['Konfidenz']:.2f}")

    return df
