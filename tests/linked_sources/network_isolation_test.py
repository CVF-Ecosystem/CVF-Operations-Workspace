from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path

os.environ["GIT_ALLOW_PROTOCOL"] = "file"

ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / "tests" / "linked_sources"
NETWORK_PREFIXES = ("http://", "https://", "ssh://", "git@")
PROCESS_CALLS = {
    "run",
    "popen",
    "call",
    "check_call",
    "check_output",
    "getoutput",
    "getstatusoutput",
    "create_subprocess_exec",
    "create_subprocess_shell",
    "system",
    "execl",
    "execle",
    "execlp",
    "execlpe",
    "execv",
    "execve",
    "execvp",
    "execvpe",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "posix_spawn",
    "posix_spawnp",
}
GIT_CALLS = PROCESS_CALLS | {
    "git",
    "_make_git_repo",
}


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id.lower()
    if isinstance(func, ast.Attribute):
        return func.attr.lower()
    return ""


class _CommandAnalyzer(ast.NodeVisitor):
    """Resolve simple variable/list indirection and reject unsafe Git calls."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.scopes: list[dict[str, set[str]]] = [{}]
        self.alias_scopes: list[dict[str, str]] = [{}]
        self.violations: list[str] = []
        self.git_call_count = 0

    def _lookup(self, name: str) -> set[str]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return set()

    def _lookup_alias(self, name: str) -> str:
        for scope in reversed(self.alias_scopes):
            if name in scope:
                return scope[name]
        return ""

    def _resolved_call_name(self, func: ast.AST) -> str:
        if isinstance(func, ast.Name):
            return self._lookup_alias(func.id) or func.id.lower()
        if isinstance(func, ast.Attribute):
            return func.attr.lower()
        return ""

    def _values(self, node: ast.AST) -> set[str]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, ast.Name):
            return set(self._lookup(node.id))
        if isinstance(node, ast.Starred):
            return self._values(node.value)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            values: set[str] = set()
            for item in node.elts:
                values.update(self._values(item))
            return values
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._values(node.left)
            right = self._values(node.right)
            if left and right:
                return left | right | {a + b for a in left for b in right}
        if isinstance(node, ast.JoinedStr):
            parts: list[set[str]] = []
            for item in node.values:
                if isinstance(item, ast.FormattedValue):
                    values = self._values(item.value)
                else:
                    values = self._values(item)
                if not values:
                    return set()
                parts.append(values)
            combined = {""}
            for values in parts:
                combined = {a + b for a in combined for b in values}
            return combined
        return set()

    def _bind(self, target: ast.AST, values: set[str]) -> None:
        if isinstance(target, ast.Name):
            self.scopes[-1][target.id] = set(values)
        elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
            current = self._lookup(target.value.id)
            self.scopes[-1][target.value.id] = current | values
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self._bind(item, values)

    def visit_Assign(self, node: ast.Assign) -> None:
        values = self._values(node.value)
        for target in node.targets:
            self._bind(target, values)
            if isinstance(target, ast.Name):
                alias = self._resolved_call_name(node.value)
                if alias in GIT_CALLS:
                    self.alias_scopes[-1][target.id] = alias
                else:
                    self.alias_scopes[-1].pop(target.id, None)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        values = self._values(node.value) if node.value is not None else set()
        self._bind(node.target, values)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name) and isinstance(node.op, ast.Add):
            current = self._lookup(node.target.id)
            added = self._values(node.value)
            combined = current | added
            if current and added:
                combined |= {a + b for a in current for b in added}
            self.scopes[-1][node.target.id] = combined
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scopes.append({})
        self.alias_scopes.append({})
        for statement in node.body:
            self.visit(statement)
        self.alias_scopes.pop()
        self.scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in {"subprocess", "os", "asyncio"}:
            for imported in node.names:
                name = imported.name.lower()
                if name in PROCESS_CALLS:
                    self.alias_scopes[-1][imported.asname or imported.name] = name
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.attr in {"append", "extend", "insert"}
        ):
            current = self._lookup(node.func.value.id)
            added: set[str] = set()
            for argument in node.args:
                added.update(self._values(argument))
            self.scopes[-1][node.func.value.id] = current | added

        name = self._resolved_call_name(node.func)
        values: set[str] = set()
        for argument in node.args:
            values.update(self._values(argument))
        for keyword in node.keywords:
            values.update(self._values(keyword.value))
        lowered = {value.lower() for value in values}

        if name in GIT_CALLS:
            command_values: set[str] = set()
            if node.args:
                command_values.update(self._values(node.args[0]))
            for keyword in node.keywords:
                if keyword.arg == "args":
                    command_values.update(self._values(keyword.value))
            shell_git = any(
                value.strip().startswith("git ")
                or " git " in f" {value.strip()} "
                for value in {item.lower() for item in command_values}
            )
            is_git_call = (
                "git" in {value.lower() for value in command_values}
                or shell_git
                or name in {"git", "_make_git_repo"}
            )
            if is_git_call:
                self.git_call_count += 1
            has_network = any(
                any(prefix in value for prefix in NETWORK_PREFIXES)
                for value in lowered
            )
            force_push = (
                ("push" in lowered or any(" push " in f" {value} " for value in lowered))
                and any(
                    flag in value
                    for value in lowered
                    for flag in ("-f", "--force", "--force-with-lease")
                )
            )
            any_set_url = "remote" in lowered and "set-url" in lowered
            network_remote_add = (
                "remote" in lowered and "add" in lowered and has_network
            )
            network_operation = is_git_call and has_network
            helper_network_remote = name == "_make_git_repo" and has_network
            unresolved_process_call = (
                name in PROCESS_CALLS
                and not command_values
            )
            if (
                force_push
                or any_set_url
                or network_remote_add
                or network_operation
                or helper_network_remote
                or unresolved_process_call
            ):
                self.violations.append(
                    f"{self.label}:{getattr(node, 'lineno', '?')}"
                )

        self.generic_visit(node)


def find_violations(source: str, label: str = "<probe>") -> list[str]:
    tree = ast.parse(source, filename=label)
    analyzer = _CommandAnalyzer(label)
    analyzer.visit(tree)
    return analyzer.violations


def analyze(source: str, label: str) -> _CommandAnalyzer:
    tree = ast.parse(source, filename=label)
    analyzer = _CommandAnalyzer(label)
    analyzer.visit(tree)
    return analyzer


class LinkedSourceNetworkIsolationTests(unittest.TestCase):
    def test_no_test_can_configure_or_invoke_a_live_git_remote(self) -> None:
        violations: list[str] = []
        for path in sorted(TEST_ROOT.glob("*_test.py")):
            violations.extend(
                find_violations(path.read_text(encoding="utf-8"), path.name)
            )
        self.assertEqual(
            violations,
            [],
            "linked-source tests contain live-remote or force-push commands: "
            + ", ".join(violations),
        )

    def test_variable_indirection_cannot_bypass_guard(self) -> None:
        cases = (
            """
LIVE = "https://github.com/example/repo.git"
subprocess.run(["git", "remote", "set-url", "origin", LIVE])
""",
            """
LIVE = "https://github.com/example/repo.git"
COMMAND = ["git", "push", LIVE, "HEAD:main"]
subprocess.run(COMMAND)
""",
            """
FORCE = "--force"
COMMAND = ["git", "push", FORCE, "origin", "HEAD:main"]
subprocess.run(COMMAND)
""",
            """
LIVE = "https://github.com/example/repo.git"
COMMAND = ["git", "push"] + [LIVE, "HEAD:main"]
subprocess.run(COMMAND)
""",
            """
LIVE = "https://github.com/example/repo.git"
COMMAND = ["git", "push"]
COMMAND += [LIVE, "HEAD:main"]
subprocess.run(COMMAND)
""",
            """
LIVE = "https://github.com/example/repo.git"
COMMAND = ["git", "push"]
COMMAND.append(LIVE)
COMMAND.append("HEAD:main")
subprocess.run(COMMAND)
""",
            """
LIVE = "https://github.com/example/repo.git"
runner = subprocess.run
runner(["git", "push", LIVE, "HEAD:main"])
""",
            """
LIVE = "https://github.com/example/repo.git"
COMMAND = ["git", "push"]
COMMAND[2:] = [LIVE, "HEAD:main"]
subprocess.run(COMMAND)
""",
            """
LIVE = "https://github.com/example/repo.git"
def execute(cmd):
    subprocess.run(cmd, cwd=".")
execute(["git", "push", LIVE, "HEAD:main"])
""",
            """
LIVE = "https://github.com/example/repo.git"
from subprocess import run as execute
execute(["git", "push", LIVE, "HEAD:main"])
""",
            """
LIVE = "https://github.com/example/repo.git"
subprocess.call(["git", "push", LIVE, "HEAD:main"])
""",
            """
LIVE = "https://github.com/example/repo.git"
os.system("git push " + LIVE)
""",
            """
LIVE = "https://github.com/example/repo.git"
subprocess.getoutput("git push " + LIVE)
""",
            """
LIVE = "https://github.com/example/repo.git"
subprocess.getstatusoutput("git push " + LIVE)
""",
            """
LIVE = "https://github.com/example/repo.git"
asyncio.create_subprocess_exec("git", "push", LIVE)
""",
            """
LIVE = "https://github.com/example/repo.git"
asyncio.create_subprocess_shell("git push " + LIVE)
""",
            """
LIVE = "https://github.com/example/repo.git"
os.posix_spawnp("git", ["git", "push", LIVE], {})
""",
            """
LIVE = "https://github.com/example/repo.git"
from os import posix_spawnp as launch
launch("git", ["git", "push", LIVE], {})
""",
            """
os.system("git push https://github.com/example/repo.git")
""",
            """
subprocess.getoutput("git push https://github.com/example/repo.git")
""",
            """
asyncio.create_subprocess_shell(
    "git push https://github.com/example/repo.git"
)
""",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertTrue(find_violations(source))

    def test_git_executing_modules_enforce_file_protocol_only(self) -> None:
        for path in sorted(TEST_ROOT.glob("*_test.py")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(name=path.name):
                self.assertIn(
                    'os.environ["GIT_ALLOW_PROTOCOL"] = "file"',
                    source,
                )


if __name__ == "__main__":
    unittest.main()
