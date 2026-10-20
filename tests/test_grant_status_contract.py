from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _checkout(tmp_path: Path) -> Path:
    target = tmp_path / "crystal"
    shutil.copytree(ROOT, target, copy_function=shutil.copy2, ignore=shutil.ignore_patterns(".git"))
    return target


def _run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/check_docs_status.sh"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("field", "invalid", "diagnostic"),
    [
        ("under_review", True, "grant review"),
        ("decision", "AWARDED", "grant decision"),
        ("award_status", "AWARDED", "grant award status"),
        ("decision_date", "2026-10-10", "grant decision date"),
        ("submitted", False, "grant submitted"),
        ("awarded", True, "grant awarded"),
    ],
)
def test_docs_status_rejects_incorrect_final_grant_fields(
    tmp_path: Path, field: str, invalid: object, diagnostic: str
) -> None:
    root = _checkout(tmp_path)
    path = root / "docs/status/implementation-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["grant"][field] = invalid
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    result = _run_checker(root)
    assert result.returncode != 0
    assert diagnostic in result.stdout


@pytest.mark.parametrize(
    "relative",
    ["docs/GRANT_NLNET_SCOPE.md", "README.ja.md", "docs/ru/GRANT_OVERVIEW.md"],
)
def test_docs_status_rejects_stale_current_grant_surface(tmp_path: Path, relative: str) -> None:
    root = _checkout(tmp_path)
    path = root / relative
    text = path.read_text(encoding="utf-8")
    # Keep the correct current overlay intact: merely appending an old claim
    # must fail too. README.ja.md already contains one permitted frozen literal.
    path.write_text(text + "\nNLnet is under review.\n", encoding="utf-8")
    result = _run_checker(root)
    assert result.returncode != 0
    assert relative in result.stdout
    assert "stale current-state phrase" in result.stdout


def test_docs_status_accepts_current_grant_and_frozen_history() -> None:
    result = _run_checker(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    historical = (ROOT / "docs/architecture/READER_RC10_RETRIEVAL_REUSE_PREREGISTRATION.md").read_text()
    assert "submitted / under review / not awarded" in historical
