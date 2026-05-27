"""Repository zum Laden und Speichern von Studiendaten als JSON."""

import json
from datetime import date
from domain import (
    Pruefungsleistung,
    Modul,
    Semester,
    Studiengang,
)


class DatenRepository:
    """Speichert und lädt Studiendaten in JSON-Dateien."""

    def laden(self, dateipfad: str) -> Studiengang:
        """Liest eine JSON-Datei und gibt ein Studiengang-Objekt zurück."""
        with open(dateipfad, "r", encoding="utf-8") as datei:
            daten = json.load(datei)

        return self._studiengang_aus_json(daten)

    def speichern(
        self, studiengang: Studiengang, dateipfad: str
    ) -> None:
        """Speichert ein Studiengang-Objekt als JSON-Datei."""
        daten = self._studiengang_zu_json(studiengang)
        with open(dateipfad, "w", encoding="utf-8") as datei:
            json.dump(daten, datei, indent=2, ensure_ascii=False)

    # --- Deserialisierung ---

    def _pruefung_aus_json(self, daten: dict) -> Pruefungsleistung:
        """Erzeugt eine Prüfungsleistung aus JSON-Daten."""
        return Pruefungsleistung(
            name=daten["name"],
            ects_punkte=daten["ectsPunkte"],
            datum=daten["datum"],
            note=daten["note"],
        )

    def _modul_aus_json(self, daten: dict) -> Modul:
        """Erzeugt ein Modul aus JSON-Daten."""
        pruefungen = [
            self._pruefung_aus_json(pl) for pl in daten["pruefungsleistungen"]
        ]
        return Modul(
            name=daten["name"],
            modulart=daten["modulart"],
            pruefungsleistungen=pruefungen,
        )

    def _semester_aus_json(self, daten: dict) -> Semester:
        """Erzeugt ein Semester aus JSON-Daten."""
        module = [self._modul_aus_json(m) for m in daten["module"]]
        return Semester(
            nummer=daten["nummer"],
            module=module,
        )

    def _studiengang_aus_json(self, daten: dict) -> Studiengang:
        """Erzeugt einen Studiengang aus JSON-Daten."""
        semester = [self._semester_aus_json(s) for s in daten["semester"]]

        start_datum = None
        if daten.get("startDatum"):
            jahr, monat, tag = daten["startDatum"].split("-")
            start_datum = date(int(jahr), int(monat), int(tag))

        return Studiengang(
            start_datum=start_datum,
            ziel_studienzeit_monate=daten.get(
                "zielStudienzeitMonate", 36
            ),
            ziel_notendurchschnitt=daten.get("zielNotendurchschnitt", 2.0),
            semester=semester,
        )

    # --- Serialisierung ---

    def _pruefung_zu_json(self, pruefung: Pruefungsleistung) -> dict:
        """Konvertiert eine Prüfungsleistung in ein JSON-Dict."""
        return {
            "name": pruefung.name,
            "ectsPunkte": pruefung.ects_punkte,
            "datum": pruefung.datum,
            "note": pruefung.note,
        }

    def _modul_zu_json(self, modul: Modul) -> dict:
        """Konvertiert ein Modul in ein JSON-Dict."""
        return {
            "name": modul.name,
            "modulart": modul.modulart,
            "pruefungsleistungen": [
                self._pruefung_zu_json(pl) for pl in modul.pruefungsleistungen
            ],
        }

    def _semester_zu_json(self, sem: Semester) -> dict:
        """Konvertiert ein Semester in ein JSON-Dict."""
        return {
            "nummer": sem.nummer,
            "module": [self._modul_zu_json(m) for m in sem.module],
        }

    def _studiengang_zu_json(self, sg: Studiengang) -> dict:
        """Konvertiert einen Studiengang in ein JSON-Dict."""
        start_str = ""
        if sg.start_datum:
            start_str = sg.start_datum.isoformat()

        return {
            "startDatum": start_str,
            "zielStudienzeitMonate": sg.ziel_studienzeit_monate,
            "zielNotendurchschnitt": sg.ziel_notendurchschnitt,
            "semester": [self._semester_zu_json(s) for s in sg.semester],
        }
