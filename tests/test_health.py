import os
import os.path

from smb.smb_structs import OperationFailure

import pyndows
from pyndows.testing import samba_mock, SMBConnectionMock, mock_pyndows_health_datetime


def test_pass_health_check(samba_mock: SMBConnectionMock, mock_pyndows_health_datetime):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
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


def test_fail_health_check(samba_mock: SMBConnectionMock, mock_pyndows_health_datetime):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    def raise_exception(*args):
        raise OperationFailure("Mock for echo failure.", [])

    samba_mock.add_callback("echo", raise_exception)
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
