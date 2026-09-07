"""
Récupération du texte brut de la page de détail d'un marché.

Sources actives :
- ONMP : page dynamique via Playwright
- TUNEPS : si certificat configuré → page détail complète
           sinon → métadonnées API uniquement
"""

from playwright.sync_api import sync_playwright

from app.core.config import settings


def _normalize_text(text):
    if not text:
        return ""
    return " ".join(text.split())


def fetch_onmp_detail_text(lien):
    """ONMP : page dynamique, lecture via Playwright."""
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
        print(f"[detail_fetcher] Échec récupération ONMP ({lien}) : {exc}")
        return ""


def _tuneps_cert_available():
    """Vérifie si le certificat TUNEPS est configuré et existe."""
    import os
    cert_path = (settings.TUNEPS_CERT_PATH or "").strip()
    cert_pass = settings.TUNEPS_CERT_PASSWORD or ""

    if not cert_path or not cert_pass:
        return False

    if not os.path.exists(cert_path):
        print(f"[detail_fetcher] ⚠️ TUNEPS_CERT_PATH configuré mais fichier introuvable : {cert_path}")
        return False

    return True


def fetch_tuneps_detail_text(lien):
    """
    TUNEPS : tente de lire la page détail.

    - Avec certificat : ouvre la page Angular → extrait budget, procédure, etc.
    - Sans certificat : retourne "" → l'IA génère une description depuis les métadonnées.
    """
    if not lien:
        return ""

    # Sans certificat → pas de page détail accessible
    if not _tuneps_cert_available():
        return ""

    # Avec certificat → tenter l'extraction
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    f"--client-certificate={settings.TUNEPS_CERT_PATH}",
                ],
            )
            try:
                context = browser.new_context(
                    ignore_https_errors=True,
                )
                page = context.new_page()
                page.goto(lien, wait_until="networkidle", timeout=45_000)

                text = _normalize_text(page.inner_text("body"))

                if text and len(text) > 100:
                    print(f"[detail_fetcher] ✅ Détail TUNEPS récupéré ({len(text)} chars)")
                    return text
                else:
                    print("[detail_fetcher] Page détail TUNEPS vide ou trop courte")
                    return ""

            finally:
                browser.close()

    except Exception as exc:
        print(f"[detail_fetcher] Échec détail TUNEPS ({lien}) : {exc}")
        return ""


def fetch_detail_text(source, lien):
    if source == "onmp":
        return fetch_onmp_detail_text(lien)
    if source == "tuneps":
        return fetch_tuneps_detail_text(lien)
    return ""