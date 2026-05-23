"""Helpers for building export file names."""

import hashlib
import re
from datetime import datetime


MAX_EXPORT_FILENAME_STEM_LENGTH = 180


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("._-") or "all"


def _fit_export_filename_stem(prefix: str, suffix: str, date_stamp: str) -> str:
    stem = f"{prefix}{suffix}_{date_stamp}"
    if len(stem) <= MAX_EXPORT_FILENAME_STEM_LENGTH:
        return stem

    digest = hashlib.sha1(stem.encode("utf-8")).hexdigest()[:8]
    tail = f"_{digest}_{date_stamp}"
    max_suffix_length = MAX_EXPORT_FILENAME_STEM_LENGTH - len(prefix) - len(tail)
    if max_suffix_length < 1:
        return f"{prefix}{digest}_{date_stamp}"[:MAX_EXPORT_FILENAME_STEM_LENGTH]

    short_suffix = suffix[:max_suffix_length].rstrip("._-") or "locations"
    return f"{prefix}{short_suffix}{tail}"


def build_export_filename(locations: str, custom_search_url: str) -> str:
    """Build a filesystem-safe base filename for TSV/JSON/XLSX exports."""
    date_stamp = datetime.now().strftime("%Y-%m-%d")
    if custom_search_url:
        suffix = "custom_search"
    else:
        suffix = _slugify((locations or "all").replace(",", "_"))

    return _fit_export_filename_stem("olx_", suffix, date_stamp)
