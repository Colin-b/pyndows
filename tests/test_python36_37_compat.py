import os

from pyndows.testing import SMBConnectionMock


def test_custom_is_file(monkeypatch):
    def failing_is_file(*args):
        raise ValueError

    monkeypatch.setattr(os.path, "isfile", failing_is_file)
    assert SMBConnectionMock._is_file(b"") is False
