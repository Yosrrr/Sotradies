"""
Récupération du texte brut de la page de détail d'un marché.

Sources :
- ONMP : page dynamique via Playwright
- TUNEPS : 3 modes d'accès (Local Server, certificat .p12, ou métadonnées)
"""

import os
import socket

from playwright.sync_api import sync_playwright

from app.core.config import settings


def _normalize_text(text):
    if not text:
        return ""
    return " ".join(text.split())


def fetch_onmp_detail_text(lien):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(lien, wait_until="networkidle", timeout=30_000)
                return _normalize_text(page.inner_text("body"))
            finally:
                browser.close()
    except Exception as exc:
        print(f"[detail_fetcher] Échec ONMP ({lien}) : {exc}")
        return ""


def _tuneps_local_server_available():
    try:
        sock = socket.create_connection(("localhost", 28080), timeout=2)
        sock.close()
        return True
    except (ConnectionRefusedError, OSError, TimeoutError):
        return False


def _tuneps_cert_available():
    cert_path = (settings.TUNEPS_CERT_PATH or "").strip()
    cert_pass = settings.TUNEPS_CERT_PASSWORD or ""
    if not cert_path or not cert_pass:
        return False
    if not os.path.exists(cert_path):
        return False
    return True


def _fetch_tuneps_authenticated(lien):
    """
    Ouvre la page détail TUNEPS avec un navigateur authentifié.

    Fonctionne si :
    - le TUNEPS Local Server tourne (clé USB branchée), ou
    - un certificat .p12 est configuré.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--ignore-certificate-errors"],
        )
        try:
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # Charger la page d'accueil pour déclencher l'authentification
            page.goto(
                "https://www.tuneps.tn",
                wait_until="networkidle",
                timeout=30_000,
            )
            page.wait_for_timeout(3000)

            # Aller sur la page détail
            page.goto(lien, wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(3000)

            text = _normalize_text(page.inner_text("body"))

            if text and len(text) > 100:
                print(f"[detail_fetcher] ✅ Détail TUNEPS authentifié ({len(text)} chars)")
                return text

            print("[detail_fetcher] Page détail TUNEPS vide ou trop courte")
            return ""

        finally:
            browser.close()


def fetch_tuneps_detail_text(lien):
    """
    TUNEPS — 3 modes :
    1. Local Server détecté → accès authentifié
    2. Certificat .p12 → accès authentifié
    3. Rien → retourne "" → description minimale depuis métadonnées
    """
    if not lien:
        return ""

    if _tuneps_local_server_available():
        print("[detail_fetcher] TUNEPS Local Server détecté")
        try:
            return _fetch_tuneps_authenticated(lien)
        except Exception as exc:
            print(f"[detail_fetcher] Échec Local Server : {exc}")

    if _tuneps_cert_available():
        print("[detail_fetcher] Certificat TUNEPS détecté")
        try:
            return _fetch_tuneps_authenticated(lien)
        except Exception as exc:
            print(f"[detail_fetcher] Échec certificat : {exc}")

    return ""


def fetch_detail_text(source, lien):
    if source == "onmp":
        return fetch_onmp_detail_text(lien)
    if source == "tuneps":
        return fetch_tuneps_detail_text(lien)
    return ""