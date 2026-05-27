"""Controller für das Studien-Dashboard."""

from datetime import date

from repository import DatenRepository
from domain import Studiengang


class DashboardController:
    """Steuert den Datenfluss zwischen Repository und View."""

    def __init__(self, repository: DatenRepository) -> None:
        """Initialisiert den Controller mit einem Repository."""
        self.repository = repository

    def lade_daten(self, dateipfad: str) -> Studiengang:
        """Lädt Studiendaten aus einer JSON-Datei."""
        return self.repository.laden(dateipfad)

    def speichere_daten(
        self, studiengang: Studiengang, dateipfad: str
    ) -> None:
        """Speichert Studiendaten in eine JSON-Datei."""
        self.repository.speichern(studiengang, dateipfad)

    def get_dashboard_daten(
        self, studiengang: Studiengang
    ) -> dict:
        """Berechnet alle KPIs und gibt sie als Dictionary zurück."""
        erreichte_ects = studiengang.erreichte_ects_gesamt()
        durchschnitt = studiengang.durchschnittsnote()

        semester_fortschritt = []
        for sem in studiengang.semester:
            semester_fortschritt.append({
                "nummer": sem.nummer,
                "erreichte_ects": sem.erreichte_ects(),
                "gesamt_ects": sem.gesamt_ects,
                "ist_abgeschlossen": sem.ist_abgeschlossen,
            })

        offene_pruefungen = []
        for sem in studiengang.semester:
            for modul in sem.module:
                for pruefung in modul.pruefungsleistungen:
                    if not pruefung.ist_bestanden:
                        offene_pruefungen.append({
                            "name": pruefung.name,
                            "modul": modul.name,
                            "semester": sem.nummer,
                            "ects": pruefung.ects_punkte,
                            "datum": pruefung.datum,
                        })

        # Berechne Start- und Zieldatum als formatierte Strings
        _MONATE = {"01": "Jan", "02": "Feb", "03": "Mär", "04": "Apr",
                   "05": "Mai", "06": "Jun", "07": "Jul", "08": "Aug",
                   "09": "Sep", "10": "Okt", "11": "Nov", "12": "Dez"}

        def _format_dt(d: date) -> str:
            return f"{_MONATE[d.strftime('%m')]} {d.year}"

        start_str = _format_dt(studiengang.start_datum) if studiengang.start_datum else ""
        ziel_str = ""
        if studiengang.start_datum:
            sd = studiengang.start_datum
            zm = studiengang.ziel_studienzeit_monate
            zj = sd.year + (sd.month - 1 + zm) // 12
            zm_monat = (sd.month - 1 + zm) % 12 + 1
            ziel_str = _format_dt(date(zj, zm_monat, sd.day))

        return {
            "hochschule": studiengang.hochschule,
            "studiengang_name": studiengang.name,
            "start_datum": start_str,
            "zieldatum": ziel_str,
            "erreichte_ects": erreichte_ects,
            "gesamt_ects": studiengang.gesamt_ects,
            "ects_prozentsatz": round(
                erreichte_ects / studiengang.gesamt_ects * 100, 1
            ),
            "durchschnittsnote": durchschnitt,
            "ziel_notendurchschnitt": studiengang.ziel_notendurchschnitt,
            "verstrichene_monate": studiengang.verstrichene_zeit_monate(),
            "ziel_monate": studiengang.ziel_studienzeit_monate,
            "verbleibende_ects": studiengang.verbleibende_ects(),
            "ist_zeit_ziel_erreichbar": studiengang.ist_zeit_ziel_erreichbar(),
            "ist_notenziel_erreichbar": studiengang.ist_notenziel_erreichbar(),
            "ist_abgeschlossen": studiengang.ist_abgeschlossen,
            "semester_fortschritt": semester_fortschritt,
            "offene_pruefungen": offene_pruefungen,
        }
