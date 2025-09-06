from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager


class TestReportSuite:
    @pytest.mark.parametrize(
        "params",
        (
                None,
                " --port 5433",
                " --run-system=false",
                " --run-postgres=false",
                " --disable-sudo",
                " -w rep1.txt",
                " --report-path=rep2.txt",
        )
    )
    @pytest.mark.bash
    def test_report(self, mamonsu_container: 'DockerManager', params) -> None:
        exit_code, output = mamonsu_container("mamonsu report" + (params or ''))
        assert exit_code == 0
