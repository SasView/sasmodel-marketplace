"""The {% deployed_version %} tag: which commit this copy of the site is running.

The deploy script on danse2 writes a DEPLOYED file ("<sha> <branch> <date>") into
the project root and then restarts gunicorn, so reading it once per process is
enough. A checkout that was never deployed has no file and shows "version unknown".
"""
from functools import lru_cache
from pathlib import Path

from django import template
from django.utils.html import format_html

register = template.Library()

REPO_URL = "https://github.com/SasView/sasmodel-marketplace"
# marketplace/templatetags/deploy_info.py -> the project root, beside manage.py
DEPLOYED_FILE = Path(__file__).resolve().parents[2] / "DEPLOYED"


@lru_cache(maxsize=None)
def read_deployed():
    try:
        sha, branch, date = DEPLOYED_FILE.read_text().split()[:3]
    except (OSError, ValueError):
        return None
    return sha, branch, date


@register.simple_tag
def deployed_version():
    info = read_deployed()
    if info is None:
        return "version unknown"
    sha, branch, date = info
    return format_html('<a href="{}/commit/{}">{}</a> ({}, deployed {})',
                       REPO_URL, sha, sha[:7], branch, date[:10])
