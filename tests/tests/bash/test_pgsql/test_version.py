import pytest

from mamonsu.plugins.pgsql.driver.version import extract_version

class TestVersion:
    @pytest.mark.parametrize("raw, expected", [
        ("14.6", "14.6"),
        ("17.2", "17.2"),
        ("9.3.10", "9.3.10"),
        ("15.1 (Debian 15.1-1.pgdg110+1)", "15.1"),
        ("15.1 (Ubuntu 15.1-1.pgdg22.04+1)", "15.1"),
        ("11.2-YB-2.17.3.0-b0", "11.2"),
        ("1.2-xxx", "1.2"),
        ("17.10 - TRIAL", "17.10"),
        ("16.14-TRIAL", "16.14"),
        ("16beta1", "16"),
        ("17.1rc1", "17.1"),
        ("12devel", "12"),
        ("16.14/TRIAL", "16.14"),
        ("", ""),
    ])
    def test_extract_version(self, raw, expected):
        assert extract_version(raw) == expected
