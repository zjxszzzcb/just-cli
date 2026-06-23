"""Tests for repo management."""
import subprocess
import shutil
import tempfile

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from testing import describe, it, expect, run_tests


def _make_fake_repo(path: Path) -> None:
    """Create a minimal git repo."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(path), capture_output=True,
    )
    (path / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=str(path), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(path), capture_output=True,
    )


@describe("Repo Manager")
class RepoManagerTests:

    @it("add_repo clones a git repo successfully")
    def test_add_repo(self):
        from just.core.repo.manager import add_repo

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_remote = Path(tmpdir) / "remote"
            _make_fake_repo(fake_remote)

            repo_path = add_repo("test-repo", str(fake_remote))
            try:
                expect(repo_path.exists()).to_be_true()
                expect((repo_path / ".git").exists()).to_be_true()
            finally:
                shutil.rmtree(repo_path, ignore_errors=True)

    @it("add_repo raises ValueError when name already exists")
    def test_add_repo_duplicate(self):
        from just.core.repo.manager import add_repo

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_remote = Path(tmpdir) / "remote"
            _make_fake_repo(fake_remote)

            repo_path = add_repo("dup-repo", str(fake_remote))
            try:
                error_raised = False
                try:
                    add_repo("dup-repo", str(fake_remote))
                except ValueError:
                    error_raised = True
                expect(error_raised).to_be_true()
            finally:
                shutil.rmtree(repo_path, ignore_errors=True)

    @it("remove_repo deletes an existing repo")
    def test_remove_repo(self):
        from just.core.repo.manager import add_repo, remove_repo

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_remote = Path(tmpdir) / "remote"
            _make_fake_repo(fake_remote)

            repo_path = add_repo("rm-repo", str(fake_remote))
            expect(repo_path.exists()).to_be_true()

            remove_repo("rm-repo")
            expect(repo_path.exists()).to_be_false()

    @it("remove_repo raises ValueError for non-existent repo")
    def test_remove_repo_missing(self):
        from just.core.repo.manager import remove_repo

        error_raised = False
        try:
            remove_repo("nonexistent-repo-xyz")
        except ValueError:
            error_raised = True
        expect(error_raised).to_be_true()

    @it("list_repos returns empty list when no repos")
    def test_list_repos_empty(self):
        from just.core.repo.manager import list_repos
        from just.core.config import get_repo_dir

        repo_dir = get_repo_dir()
        if not repo_dir.exists():
            result = list_repos()
            expect(result).to_have_length(0)

    @it("_get_repo_info extracts correct metadata")
    def test_repo_info(self):
        from just.core.repo.manager import _get_repo_info

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = Path(tmpdir) / "info-repo"
            _make_fake_repo(fake_repo)

            (fake_repo / "commands").mkdir()
            (fake_repo / "installers").mkdir()

            info = _get_repo_info(fake_repo)
            expect(info["name"]).to_equal("info-repo")
            expect(info["has_commands"]).to_be_true()
            expect(info["has_installers"]).to_be_true()
            # Default branch could be master or main
            expect(info["branch"] in ("master", "main")).to_be_true()


if __name__ == "__main__":
    run_tests()
