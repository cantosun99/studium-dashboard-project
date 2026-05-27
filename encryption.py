"""Verschlüsselung von Studiendaten mit Fernet (AES)."""

import base64
import hashlib
from cryptography.fernet import Fernet


def _key_from_passwort(passwort: str) -> bytes:
    """Leitet einen Fernet-Schlüssel aus einem Passwort ab."""
    return hashlib.sha256(passwort.encode("utf-8")).digest()


def _fernet(passwort: str) -> Fernet:
    """Erzeugt eine Fernet-Instanz aus einem Passwort."""
    return Fernet(base64.urlsafe_b64encode(_key_from_passwort(passwort)))


def verschluesseln(text: str, passwort: str) -> bytes:
    """Verschlüsselt einen Text mit dem gegebenen Passwort."""
    return _fernet(passwort).encrypt(text.encode("utf-8"))


def entschlüsseln(verschlüsselt: bytes, passwort: str) -> str:
    """Entschlüsselt den Text mit dem gegebenen Passwort."""
    return _fernet(passwort).decrypt(verschlüsselt).decode("utf-8")


def datei_verschluesseln(eingabe_pfad: str, ausgabe_pfad: str,
                         passwort: str) -> None:
    """Liest eine Textdatei, verschlüsselt sie und speichert das Ergebnis."""
    with open(eingabe_pfad, "r", encoding="utf-8") as f:
        inhalt = f.read()
    with open(ausgabe_pfad, "wb") as f:
        f.write(verschluesseln(inhalt, passwort))


def datei_entschlüsseln(dateipfad: str, passwort: str) -> str:
    """Liest eine verschlüsselte Datei und gibt den entschlüsselten Text zurück."""
    with open(dateipfad, "rb") as f:
        return entschlüsseln(f.read(), passwort)


def _get_data_path(name: str) -> str:
    """Liefert den Pfad zu einer mitgelieferten Daten-Datei.

    Funktioniert sowohl im normalen Betrieb als auch in der
    mit PyInstaller gepackten .exe (Single-File-Modus).
    """
    import os
    import sys

    if getattr(sys, "frozen", False):
        # PyInstaller Single-File: Dateien liegen im temporären _MEIPASS-Verzeichnis
        basis = getattr(sys, "_MEIPASS", "")
    else:
        basis = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(basis, name)


def get_encrypted_data_path() -> str:
    """Pfad zur verschlüsselten Studiendaten-Datei."""
    return _get_data_path("studien_daten.enc")


def get_template_data_path() -> str:
    """Pfad zur leeren Vorlagen-Datei."""
    return _get_data_path("studien_daten_vorlage.json")
