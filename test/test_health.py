import os
import os.path

import pyndows
from pyndows.mock import samba_mock


class DateTimeMock:
    @staticmethod
    def utcnow():
        class UTCDateTimeMock:
            @staticmethod
            def isoformat():
                return "2018-10-11T15:05:05.663979"

        return UTCDateTimeMock


def test_pass_health_check(samba_mock, monkeypatch):
    monkeypatch.setattr(pyndows._windows, "datetime", DateTimeMock)
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.echo_responses[b""] = b""
    assert pyndows.health_details("test", connection) == (
        "pass",
        {
            "test:echo": {
                "componentType": "TestComputer",
                "observedValue": "",
                "status": "pass",
                "time": "2018-10-11T15:05:05.663979",
            }
        },
    )


def test_fail_health_check(samba_mock, monkeypatch):
    monkeypatch.setattr(pyndows._windows, "datetime", DateTimeMock)
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    assert pyndows.health_details("test", connection) == (
        "fail",
        {
            "test:echo": {
                "componentType": "TestComputer",
                "status": "fail",
                "time": "2018-10-11T15:05:05.663979",
                "output": f"Mock for echo failure.{os.linesep}",
            }
        },
    )
