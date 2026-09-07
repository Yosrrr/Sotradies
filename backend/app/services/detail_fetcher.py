"""
Récupération du texte brut de la page de détail d'un marché.

Sources actives :
- ONMP : page dynamique via Playwright
- TUNEPS : métadonnées API suffisantes (pas de fetch détail)
"""

from playwright.sync_api import sync_playwright


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


def fetch_detail_text(source, lien):
    if source == "onmp":
        return fetch_onmp_detail_text(lien)
    if source == "tuneps":
        return ""
    return ""