import os
import os.path

import pyndows
from pyndows.testing import samba_mock, SMBConnectionMock


class DateTimeMock:
    @staticmethod
    def utcnow():
        class UTCDateTimeMock:
            @staticmethod
            def isoformat():
                return "2018-10-11T15:05:05.663979"

        return UTCDateTimeMock


def test_pass_health_check(samba_mock: SMBConnectionMock, monkeypatch):
    monkeypatch.setattr(pyndows._windows, "datetime", DateTimeMock)
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.echo_responses[b""] = b""
    assert pyndows.check("tests", connection) == (
        "pass",
        {
            "tests:echo": {
                "componentType": "TestComputer",
                "observedValue": "",
                "status": "pass",
                "time": "2018-10-11T15:05:05.663979",
            }
        },
    )


def test_fail_health_check(samba_mock: SMBConnectionMock, monkeypatch):
    monkeypatch.setattr(pyndows._windows, "datetime", DateTimeMock)
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    assert pyndows.check("tests", connection) == (
        "fail",
        {
            "tests:echo": {
                "componentType": "TestComputer",
                "status": "fail",
                "time": "2018-10-11T15:05:05.663979",
                "output": f"Mock for echo failure.{os.linesep}",
            }
        },
    )
