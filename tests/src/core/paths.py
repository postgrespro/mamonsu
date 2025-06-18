from pathlib import Path


def _find_tests_root() -> Path:
    current = Path(__file__).absolute()
    for parent in current.parents:
        if (parent / "mmns_pg.Dockerfile").exists() or (parent / "pytest.ini").exists():
            return parent
    raise FileNotFoundError("Project root not found")


class ProjectPaths:
    TESTS_ROOT = _find_tests_root()
    MAMONSU_ROOT = TESTS_ROOT.parent

    COMPOSE_FILE = TESTS_ROOT / "docker-compose.yaml"
    METRICS_PATH = MAMONSU_ROOT / "github-actions-tests" / "sources"

