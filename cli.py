"""SENTRY-DVL Kommandozeilen-Interface"""
import argparse
import sys
import logging


def main():
    parser = argparse.ArgumentParser(
        prog="sentry-dvl",
        description="SENTRY-DVL: Dokument-Verifikations-Layer für LLM-Ausgaben",
        epilog="DOI: 10.5281/zenodo.20490643"
    )
    sub = parser.add_subparsers(dest="befehl")

    p_check = sub.add_parser("check", help="Einzelne Prüfung ausführen")
    p_check.add_argument("--kontext", required=True, help="Referenztext")
    p_check.add_argument("--antwort", required=True, help="LLM-Antwort")
    p_check.add_argument("--kein-nli", action="store_true", help="NLI-Modell deaktivieren")

    p_bench = sub.add_parser("benchmark", help="Vollständigen Benchmark ausführen")
    p_bench.add_argument("--kein-nli", action="store_true", help="NLI-Modell deaktivieren")

    sub.add_parser("info", help="Version und DOI anzeigen")

    args = parser.parse_args()

    if args.befehl == "info" or args.befehl is None:
        print("SENTRY-DVL v1.2.0")
        print("DOI: 10.5281/zenodo.20490643")
        print("Lizenz: AGPL-3.0")
        print("Autor: JoAchim Ganter")
        print("Kommerzielle Lizenz: jo.ganter@googlemail.com")
        return

    if args.befehl == "check":
        from engine import SentryDVL
        sentry = SentryDVL(mit_nli=not args.kein_nli)
        verdict = sentry.evaluieren(args.kontext, args.antwort)
        print(f"\nStatus    : {verdict.status}")
        print(f"Konfidenz : {verdict.konfidenz:.2f}")
        print(f"Checker   : {verdict.checker}")
        print(f"Begründung: {verdict.begruendung}")
        ausgabe = verdict.get_nutzer_antwort(args.antwort)
        print(f"\nNutzer sieht:\n{ausgabe}")
        sys.exit(0 if verdict.ist_sicher else 1)

    if args.befehl == "benchmark":
        from engine import SentryDVL
        from benchmark import benchmark_ausfuehren
        import pandas as pd
        sentry = SentryDVL(mit_nli=not args.kein_nli)
        benchmark_ausfuehren(sentry)


if __name__ == "__main__":
    main()
