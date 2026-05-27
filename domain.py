"""Domain-Klassen für das Studien-Dashboard."""

from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Katalog der Wahlpflichtmodule mit ihren Prüfungsleistungen.
# ERP hat nur eine Prüfung; alle anderen haben zwei.
# Schlüssel = Anzeigename, Wert = Liste der Prüfungsnamen
# ---------------------------------------------------------------------------
WAHLPFLICHT_A_B: dict[str, list[str]] = {
    "Angewandter Vertrieb": [
        "Angewandter Vertrieb I (BWAV01)",
        "Angewandter Vertrieb II (BWAV02)",
    ],
    "Apple Mobile Solution Development": [
        "Apple Mobile Solution Development I (DLAMSD01)",
        "Apple Mobile Solution Development II (DLAMSD02)",
    ],
    "Business-Controlling": [
        "Business-Controlling I (BWBC01-01)",
        "Business-Controlling II (BWBC02-01)",
    ],
    "Data Science und OOP mit Python": [
        "Einführung in Data Science (DLBDSIDS01-01_D)",
        "Projekt: OOP und funktionale Programmierung mit Python (DLBDSOOFPP01_D)",
    ],
    "E-Commerce": [
        "E-Commerce I (BWEC01-02)",
        "E-Commerce II (BWEC02-02)",
    ],
    "E-Learning": [
        "Lehren und Lernen mit digitalen Medien (DLBPGWDB01-01)",
        "Projekt: E-Learning (DLBMIEL01)",
    ],
    "Enterprise Resource Planning": [
        "Enterprise Resource Planning (DLERP01)",
    ],
    "Eventmanagement": [
        "Eventmanagement I (BWEM01)",
        "Eventmanagement II (BWEM02)",
    ],
    "Financial Services Management": [
        "Financial Services Management I (BWFS01)",
        "Financial Services Management II (BWFS02)",
    ],
    "FinTech": [
        "FinTech (Überblick und technologische Grundlagen) (DLBFMWFT01)",
        "FinTech (Disruptive und innovative Ansätze) (DLBFMWFT02)",
    ],
    "Health Care Management": [
        "Einführung in das Gesundheitsmanagement (BWGM01)",
        "Rahmenbedingungen des Gesundheitsmarktes (BWGM02)",
    ],
    "Human Computer Interaction und UX-Prototyping": [
        "Human-Computer Interaction (DLBUXHCI01)",
        "UX-Prototyping (DLBUXUXP01-01)",
    ],
    "Immobilienmanagement": [
        "Immobilienmanagement I - Einführung (BWIM01)",
        "Immobilienmanagement II - Vertiefung (BWIM02)",
    ],
    "Internationales Marketing und Branding": [
        "Internationales Marketing (BWMI01-01)",
        "Internationales Brand Management - Vertiefung (BWMI02)",
    ],
    "IT- und Medienrecht": [
        "IT-Recht (DLBIITR01-01)",
        "Medienrecht (DLBMIMR01)",
    ],
    "Logistikmanagement": [
        "Grundlagen des Logistik- und Prozessmanagements (DLBLOGLP01-01)",
        "Transport, Umschlag und Lagerung (DLBLOTUL01)",
    ],
    "Luftverkehrsmanagement": [
        "Grundlagen des Luftverkehrs (BWLM01)",
        "Netz- und Yield-Management (BWLM02)",
    ],
    "Mastering Prompts": [
        "Artificial Intelligence (DLBDSEAIS01-01_D)",
        "Projekt: AI Fluency - Einführung in die generative KI (DLBPKIEKPT01-01)",
    ],
    "Mathematik Grundlagen": [
        "Mathematik Grundlagen I (IMT101)",
        "Mathematik Grundlagen II (IMT102-01)",
    ],
    "Mathematik: Lineare Algebra & Analysis": [
        "Mathematik: Lineare Algebra (DLBBIM01)",
        "Mathematik: Analysis (DLBBIMD01)",
    ],
    "Mediendistribution": [
        "Digitale Medienformate (DLBMIDMF01)",
        "Projekt: Medienplattformen und -systeme (DLBMIMPFS01-01)",
    ],
    "Robotik und Industrie 4.0": [
        "Einführung in die Robotik (DLBROIR01-01_D)",
        "Fertigungsverfahren Industrie 4.0 (DLBINGFVI01)",
    ],
    "Search Engine Marketing": [
        "Search Engine Optimization - SEO (DLBECSEO01)",
        "Search Engine Advertising - SEA (DLBECSEA01)",
    ],
    "Statistik Grundlagen": [
        "Statistik - Wahrscheinlichkeit und deskriptive Statistik (DLBDSSPDS01_D)",
        "Statistik - Induktive Statistik (DLBDSSIS01_D)",
    ],
    "Supply Chain Management": [
        "Supply-Chain-Management I (BWSC01)",
        "Supply-Chain-Management II (BWSC02)",
    ],
    "Tourismusmanagement": [
        "Grundlagen der Tourismuswirtschaft (BWTO01-01)",
        "Akteur:innen und Geschäftsmodelle der Tourismuswirtschaft (BWTO02)",
    ],
    "Unternehmerisches Hotelmanagement": [
        "Grundlagen des Hotelmanagements (BWHO01-01)",
        "Strategisches Hotelmanagement (BWHO02-01)",
    ],
    "User Testing und Evaluation": [
        "Einführung in die Usability Evaluation (DLBUXEUT01)",
        "Projekt: Usability Evaluation (DLBUXUE01)",
    ],
}

WAHLPFLICHT_C: dict[str, list[str]] = {
    "AI Specialist": [
        "Artificial Intelligence (DLBDSEAIS01-01)",
        "Project: Artificial Intelligence (DLBDSEAIS02)",
    ],
    "Augmented, Mixed und Virtual Reality": [
        "Augmented, Mixed und Virtual Reality (DLBMIAMVR01)",
        "Projekt: X-Reality (DLBMIAMVR02)",
    ],
    "AWS Cloud Specialization": [
        "Project: AWS - Cloud Essentials (DLBPAWSCLES01)",
        "Project: AWS - Cloud Advanced (DLBPAWSCLAD01)",
    ],
    "Business Consulting": [
        "Business Consulting I (BWCN01)",
        "Business Consulting II (BWCN02)",
    ],
    "Business Intelligence": [
        "Business Intelligence (IWBI01)",
        "Projekt Business Intelligence (IWBI02)",
    ],
    "Data Engineer": [
        "Data Engineering (DLBDSEDE01)",
        "Project: Data Engineering (DLBDSEDE02)",
    ],
    "Digital Publishing und Medieninformatik": [
        "Digital Publishing (DLBMDDP01)",
        "Projekt Medieninformatik (DLBMIPMI01)",
    ],
    "Digitale Geschäftsmodelle": [
        "Digitale Business-Modelle (DLBLODB01-01)",
        "Projekt: Design Thinking (DLBINGDT01)",
    ],
    "Digitale Produktion und Smart Device": [
        "Digitalisierung in der Produktion (DLBMABWPODP01)",
        "Projekt: Smart Devices & Factory (DLBINGPSDF01)",
    ],
    "Grundlagen Webshop-Programmierung": [
        "Content Management Systeme (DLBDBCMS01)",
        "Grundlagen der Web-Programmierung (DLBECGP01)",
    ],
    "IT-Sicherheitsberatung": [
        "Technische und betriebliche IT-Sicherheitskonzeptionen (DLBCSEEISC01_D)",
        "Projekt: Einsatz und Konfiguration von SIEM-Systemen (DLBCSEEISC02_D)",
    ],
    "Karriere-Entwicklung": [
        "Persönlicher Elevator Pitch (DLBKAENT02)",
        "Persönlicher Karriereplan (DLBKAENT01)",
    ],
    "Machine Learning": [
        "Statistical Computing (DLBDBSC01)",
        "Deep Learning (DLBDBDL01)",
    ],
    "Microsoft ERP - Dynamics 365": [
        "Projekt: Dynamics 365 BC - Aufbau eines Finanzunternehmens (DLBMSERP01)",
        "Projekt: Dynamics 365 BC - Geschäftsprozesse Vertrieb (DLBMSERP02)",
    ],
    "SAP S/4HANA Business Process Integration": [
        "Project: SAP S/4HANA - Financial Company Setup (DLBSAPBPI01)",
        "Project: SAP S/4HANA - Business Processes (DLBSAPBPI02)",
    ],
    "Smart Devices": [
        "Smart Devices (DLBINGSD01)",
        "Smart Devices II (DLBINGSD02)",
    ],
    "Smart Factory": [
        "Smart Factory (DLBINGSF01)",
        "Smart Factory II (DLBINGSF02)",
    ],
    "Smart Mobility": [
        "Smart Mobility (DLBINGSM01)",
        "Smart Mobility II (DLBINGSM02)",
    ],
    "Smart Services": [
        "Smart Services (DLBINGSS01)",
        "Smart Services II (DLBINGSS02)",
    ],
    "Studium Generale": [
        "Studium Generale I (DLBSG01)",
        "Studium Generale II (DLBSG02)",
    ],
    "User Experience": [
        "User Experience (DLBMIUEX01-01)",
        "UX-Projekt (DLBMIUEX02)",
    ],
}


@dataclass
class Pruefungsleistung:
    """Stellt eine einzelne Prüfungsleistung dar."""

    name: str
    ects_punkte: int
    datum: str = "offen"
    note: float | None = None

    def __post_init__(self) -> None:
        """Validiert die Attribute nach der Initialisierung."""
        if self.note is not None and not (1.0 <= self.note <= 5.0):
            raise ValueError(f"Note muss zwischen 1,0 und 5,0 liegen: {self.note}")
        if self.ects_punkte <= 0:
            raise ValueError(f"ECTS-Punkte müssen positiv sein: {self.ects_punkte}")

    @property
    def ist_bestanden(self) -> bool:
        """Prüfung ist bestanden, wenn Datum und Note vorliegen."""
        return self.datum != "offen" and self.note is not None


@dataclass
class Modul:
    """Stellt ein Studienmodul mit Prüfungsleistungen dar."""

    name: str
    modulart: str
    pruefungsleistungen: list[Pruefungsleistung] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validiert den Modul-Typ nach der Initialisierung."""
        if self.modulart not in ("Pflicht", "Wahlpflicht"):
            raise ValueError(
                f"Modulart muss Pflicht oder Wahlpflicht sein: {self.modulart}"
            )
        if not self.pruefungsleistungen:
            raise ValueError(f"Modul '{self.name}' braucht mindestens eine Prüfung")

    def erreichte_ects(self) -> int:
        """Summe der ECTS aller bestandenen Prüfungen."""
        return sum(pl.ects_punkte for pl in self.pruefungsleistungen if pl.ist_bestanden)

    @property
    def ist_abgeschlossen(self) -> bool:
        """Modul ist abgeschlossen, wenn alle Prüfungen bestanden sind."""
        return all(pl.ist_bestanden for pl in self.pruefungsleistungen)

    @property
    def gesamt_ects(self) -> int:
        """Summe der ECTS aller Prüfungen im Modul."""
        return sum(pl.ects_punkte for pl in self.pruefungsleistungen)


@dataclass
class Semester:
    """Stellt ein Semester mit zugehörigen Modulen dar."""

    nummer: int
    module: list[Modul] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validiert die Semesternummer nach der Initialisierung."""
        if not (1 <= self.nummer <= 6):
            raise ValueError(
                f"Semesternummer muss zwischen 1 und 6 liegen: {self.nummer}"
            )

    def erreichte_ects(self) -> int:
        """Summe der erreichten ECTS über alle Module im Semester."""
        return sum(modul.erreichte_ects() for modul in self.module)

    @property
    def ist_abgeschlossen(self) -> bool:
        """Semester ist abgeschlossen, wenn alle Module abgeschlossen sind."""
        return all(modul.ist_abgeschlossen for modul in self.module)

    @property
    def gesamt_ects(self) -> int:
        """Summe der ECTS aller Module im Semester."""
        return sum(modul.gesamt_ects for modul in self.module)


@dataclass
class Studiengang:
    """Stellt den gesamten Studiengang dar."""

    hochschule: str = "IU Internationale Hochschule"
    name: str = "Bachelor of Science Softwareentwicklung"
    regel_studienzeit_monate: int = 36
    gesamt_ects: int = 180
    start_datum: date | None = None
    ziel_studienzeit_monate: int = 36
    ziel_notendurchschnitt: float = 2.0
    semester: list[Semester] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validiert die Zielwerte nach der Initialisierung."""
        if self.ziel_notendurchschnitt < 1.0 or self.ziel_notendurchschnitt > 5.0:
            raise ValueError(
                f"Ziel-Notendurchschnitt muss zwischen 1,0 und 5,0 liegen: "
                f"{self.ziel_notendurchschnitt}"
            )
        if self.ziel_studienzeit_monate <= 0:
            raise ValueError(
                f"Ziel-Studienzeit muss positiv sein: {self.ziel_studienzeit_monate}"
            )

    def erreichte_ects_gesamt(self) -> int:
        """Summe aller bestandenen ECTS über alle Semester."""
        return sum(sem.erreichte_ects() for sem in self.semester)

    def durchschnittsnote(self) -> float | None:
        """ECTS-gewichteter Durchschnitt aller bestandenen Prüfungen."""
        gewichtete_summe = 0.0
        gesamt_ects_bestanden = 0

        for sem in self.semester:
            for modul in sem.module:
                for pruefung in modul.pruefungsleistungen:
                    if pruefung.ist_bestanden:
                        gewichtete_summe += pruefung.note * pruefung.ects_punkte
                        gesamt_ects_bestanden += pruefung.ects_punkte

        if gesamt_ects_bestanden == 0:
            return None

        return round(gewichtete_summe / gesamt_ects_bestanden, 2)

    def verstrichene_zeit_monate(self) -> float:
        """Monate seit Studienstart."""
        if self.start_datum is None:
            return 0.0
        heute = date.today()
        tage = (heute - self.start_datum).days
        return round(tage / 30.44, 1)

    def verbleibende_ects(self) -> int:
        """Noch zu erreichende ECTS-Punkte."""
        return self.gesamt_ects - self.erreichte_ects_gesamt()

    def ist_zeit_ziel_erreichbar(self) -> bool:
        """Prüft, ob verbleibende ECTS in der restlichen Zeit machbar sind."""
        if self.start_datum is None:
            return True
        verstrichen = self.verstrichene_zeit_monate()
        verbleibende_zeit = max(self.ziel_studienzeit_monate - verstrichen, 0)
        if verbleibende_zeit <= 0:
            return self.verbleibende_ects() <= 0
        monatlich_braucht = self.verbleibende_ects() / verbleibende_zeit
        return monatlich_braucht <= 30

    def ist_notenziel_erreichbar(self) -> bool:
        """Prüft, ob das Notenziel theoretisch noch erreichbar ist."""
        aktuelle_note = self.durchschnittsnote()
        if aktuelle_note is None:
            return True
        erreichte = self.erreichte_ects_gesamt()
        rest_ects = self.verbleibende_ects()
        if rest_ects <= 0:
            return aktuelle_note <= self.ziel_notendurchschnitt
        gesamt_ects = erreichte + rest_ects
        erforderte_rest = (
            (self.ziel_notendurchschnitt * gesamt_ects
             - aktuelle_note * erreichte) / rest_ects
        )
        return erforderte_rest >= 1.0

    @property
    def ist_abgeschlossen(self) -> bool:
        """Studiengang ist abgeschlossen, wenn alle 180 ECTS erreicht sind."""
        return self.erreichte_ects_gesamt() >= self.gesamt_ects
