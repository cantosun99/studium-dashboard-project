"""Einstiegspunkt für das Studien-Dashboard."""

import json
import os
import sys
from tkinter import Tk, messagebox, simpledialog


def _frage_start_modus(parent=None) -> tuple[str, str]:
    """Zeigt einen Dialog: leere Vorlage oder Daten mit Key laden.

    parent: Optionaler Parent (z.B. nach customtkinter-Initialisierung).
    Wenn None wird ein temporärer Tk-Root erstellt.
    """
    own_root = None
    if parent is None:
        own_root = Tk()
        own_root.withdraw()

    wahl = messagebox.askyesno(
        "Studien-Dashboard",
        "Möchten Sie als Dozent mit Hilfe des der Installationsanleitung beiliegenden Decryption-Keys meine realen Studiendaten laden?",
    )

    if wahl:
        key = simpledialog.askstring(
            "Schlüssel eingeben",
            "Bitte geben Sie den der Installationsanleitung beiliegenden Decryption-Key ein:",
            show="*",
        )
        if own_root:
            own_root.destroy()

        if key is None or key.strip() == "":
            return "cancel", ""
        return "daten", key.strip()
    else:
        if own_root:
            own_root.destroy()
        return "vorlage", ""


def hauptprogramm() -> None:
    """Startet die Anwendung."""
    import traceback

    try:
        # 1. Prüfe, ob bereits gespeicherte Daten existieren
        gespeicherte_datei = "studien_daten.json"
        if os.path.exists(gespeicherte_datei):
            wahl = "gespeichert"
            passwort = ""
        else:
            # Dialog zeigen (BEVOR customtkinter initialisiert wird!)
            wahl, passwort = _frage_start_modus()
            if wahl == "cancel":
                return

        # 2. Erst jetzt customtkinter und Hauptfenster
        from repository import DatenRepository
        from controller import DashboardController
        from view import DashboardView
        from encryption import (
            get_encrypted_data_path,
            get_template_data_path,
            datei_entschlüsseln,
        )

        repository = DatenRepository()
        controller = DashboardController(repository)
        view = DashboardView(controller)

        if wahl == "gespeichert":
            try:
                studiengang = controller.lade_daten(gespeicherte_datei)
                view.dateipfad = gespeicherte_datei
            except Exception:
                # Gespeicherte Datei beschädigt → Dialog zeigen
                wahl, passwort = _frage_start_modus(view.root)
                if wahl == "cancel":
                    return
                if wahl == "vorlage":
                    pfad = get_template_data_path()
                    studiengang = controller.lade_daten(pfad)
                    view.dateipfad = gespeicherte_datei
                else:
                    try:
                        enc_pfad = get_encrypted_data_path()
                        json_text = datei_entschlüsseln(enc_pfad, passwort)
                        daten = json.loads(json_text)
                        studiengang = repository._studiengang_aus_json(daten)
                        view.dateipfad = gespeicherte_datei
                    except Exception as fehler:
                        messagebox.showerror(
                            "Entschlüsselung fehlgeschlagen",
                            f"Falscher Schlüssel oder Datei beschädigt.\n\n{fehler}")
                        return
        elif wahl == "vorlage":
            pfad = get_template_data_path()
            studiengang = controller.lade_daten(pfad)
            view.dateipfad = gespeicherte_datei
        else:
            try:
                enc_pfad = get_encrypted_data_path()
                json_text = datei_entschlüsseln(enc_pfad, passwort)
                daten = json.loads(json_text)
                studiengang = repository._studiengang_aus_json(daten)
                view.dateipfad = gespeicherte_datei
            except Exception as fehler:
                view._zeige_fehler(
                    "Entschlüsselung fehlgeschlagen",
                    f"Falscher Schlüssel oder Datei beschädigt.\n\n{fehler}")
                view.root.destroy()
                return

        # 3. Hauptfenster anzeigen
        view.anzeigen(studiengang)
        view.starten()

    except Exception as e:
        traceback.print_exc()
        input("Fehler aufgetreten. Drücke Enter zum Beenden...")


if __name__ == "__main__":
    hauptprogramm()
