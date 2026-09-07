"""Contrôle pré-merge : routes enregistrées, tâches Celery visibles, profil bootstrap.
À lancer avant chaque push : python -m scripts.premerge_check"""
import re, sys
from pathlib import Path

from app.main import app
from app.workers import tasks  # noqa: F401 — enregistre les tâches
from app.core.celery_app import celery_app

errors = []

routes = {r.path for r in app.routes}
for must in ["/api/admin/commercials", "/api/auth/me", "/api/admin/config"]:
    if not any(p.startswith(must) for p in routes):
        errors.append(f"Route absente : {must}")

for task in ["tasks.run_cleanup", "tasks.send_periodic_report", "tasks.run_daily_scan"]:
    if task not in celery_app.tasks:
        errors.append(f"Tâche Celery non enregistrée : {task}")

bootstrap = Path("scripts/bootstrap.py").read_text(encoding="utf-8")
if not re.search(r'profil\s*=\s*"superadmin"', bootstrap):
    errors.append('bootstrap.py ne crée pas profil="superadmin"')

if errors:
    print("❌ PRE-MERGE CHECK ÉCHOUÉ")
    for e in errors: print("  -", e)
    sys.exit(1)
print("✅ pre-merge check OK — routes, tâches Celery et bootstrap conformes")