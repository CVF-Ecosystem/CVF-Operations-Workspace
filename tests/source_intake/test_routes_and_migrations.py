from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    module_path = REPO_ROOT / "scripts" / "source_intake" / relative
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


routes_mod = _load("si_routes", "routes.py")
migrations_mod = _load("si_migrations", "migrations.py")


def _commit_fixture(repo: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "f0-test@example.com"],
        cwd=repo, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "F0 Test"],
        cwd=repo, check=True, capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"],
        cwd=repo, check=True, capture_output=True,
    )


_ROUTER_SOURCE = '''
from fastapi import APIRouter

router = APIRouter(prefix="/widgets")


@router.get("/")
async def list_widgets():
    return []


@router.post("/{widget_id}/activate")
async def activate_widget(widget_id: str):
    return {"id": widget_id}
'''


class DiscoverRoutesTests(unittest.TestCase):
    def test_discovers_routes_from_an_arbitrary_unnamed_app(self) -> None:
        # No app name is hardcoded anywhere in routes.py: this proves an
        # ingress the tool was never told about by name (a synthetic app,
        # not workspace-api or integration-edge) is still discovered.
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            router_dir = worktree / "apps" / "totally-unforeseen-app" / "src" / "widgets"
            router_dir.mkdir(parents=True)
            (router_dir / "router.py").write_text(_ROUTER_SOURCE, encoding="utf-8")

            discovered = routes_mod.discover_routes(worktree)

            self.assertEqual(len(discovered), 2)
            paths_and_methods = {(r["method"], r["path"]) for r in discovered}
            self.assertIn(("GET", "/widgets/"), paths_and_methods)
            self.assertIn(("POST", "/widgets/{widget_id}/activate"), paths_and_methods)
            for record in discovered:
                self.assertEqual(record["app"], "totally-unforeseen-app")
                self.assertNotIn("\\", record["source_path"])

    def test_no_apps_directory_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(routes_mod.discover_routes(Path(tmp)), [])

    def test_sorted_deterministic_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            for app_name in ("z-app", "a-app"):
                router_dir = worktree / "apps" / app_name / "src"
                router_dir.mkdir(parents=True)
                (router_dir / "router.py").write_text(_ROUTER_SOURCE, encoding="utf-8")
            discovered = routes_mod.discover_routes(worktree)
            apps_seen = [r["app"] for r in discovered]
            self.assertEqual(apps_seen, sorted(apps_seen))


class DiscoverMigrationsTests(unittest.TestCase):
    def test_orders_by_filename_and_hashes_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            migrations_dir = worktree / "database" / "migrations"
            migrations_dir.mkdir(parents=True)
            (migrations_dir / "002_second.sql").write_text("CREATE TABLE second();\n", encoding="utf-8")
            (migrations_dir / "001_first.sql").write_text("CREATE TABLE first();\n", encoding="utf-8")
            _commit_fixture(worktree)

            discovered = migrations_mod.discover_migrations(worktree)

            self.assertEqual(len(discovered), 2)
            self.assertTrue(discovered[0]["source_path"].endswith("001_first.sql"))
            self.assertEqual(discovered[0]["order"], 0)
            self.assertTrue(discovered[1]["source_path"].endswith("002_second.sql"))
            self.assertEqual(discovered[1]["order"], 1)

    def test_hash_changes_when_migration_content_drifts(self) -> None:
        # Proves the tool detects migration drift: identical filenames with
        # different content must yield different hashes.
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            for base, content in ((Path(tmp_a), "CREATE TABLE t (id int);\n"), (Path(tmp_b), "CREATE TABLE t (id bigint);\n")):
                migrations_dir = base / "database" / "migrations"
                migrations_dir.mkdir(parents=True)
                (migrations_dir / "001_foundation.sql").write_text(content, encoding="utf-8")
                _commit_fixture(base)

            hash_a = migrations_mod.discover_migrations(Path(tmp_a))[0]["sha256"]
            hash_b = migrations_mod.discover_migrations(Path(tmp_b))[0]["sha256"]
            self.assertNotEqual(hash_a, hash_b)

    def test_no_migrations_directory_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(migrations_mod.discover_migrations(Path(tmp)), [])


if __name__ == "__main__":
    unittest.main()
