import shutil
from typing import List
from collections import namedtuple
import datetime
import pathlib

import pytest

from smb.smb_structs import OperationFailure, SMB_FILE_ATTRIBUTE_DIRECTORY
from smb.base import SharedFile

SharedFileMock = namedtuple("SharedFileMock", ["filename", "isDirectory"])


def try_get(path: pathlib.Path, timeout=1):
    """
    Wait until the path exists to return it.

    :param path: File or Directory file path to return if exists.
    :param timeout: Maximum amount of seconds to wait
    :raises TimeoutError: in case timeout is reached and path does not exists.
    """
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() <= end:
        if path.exists():
            return path
    else:
        raise TimeoutError(f"{path.name} could not be found within {timeout} seconds.")


class SMBConnectionMock:
    """
    Mock a Samba Connection object.
    """

    tmpdir = None
    monkeypatch = None

    def __init__(self, user_name, password, test_name, machine_name, *args, **kwargs):
        self.remote_name = machine_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def connect(self, *args):
        return True

    def storeFile(self, share_drive_path: str, file_path: str, file, timeout=30) -> int:
        if self.path(share_drive_path, file_path).parent.exists():
            self.path(share_drive_path, file_path).write_bytes(file.read())
            return 0

        raise OperationFailure(
            f"Failed to store {file_path} on {share_drive_path}: Unable to open file",
            [],
        )

    def createDirectory(self, share_drive_path: str, folder_path: str, timeout=30):
        try:
            self.path(share_drive_path, folder_path).mkdir()
        except (FileNotFoundError, FileExistsError):
            raise OperationFailure(
                f"Failed to create directory {folder_path} on {share_drive_path}: Create failed",
                [],
            )

    def rename(
        self, share_drive_path: str, initial_file_path: str, new_file_path: str
    ) -> None:
        self.path(share_drive_path, initial_file_path).rename(
            self.path(share_drive_path, new_file_path)
        )

    def retrieveFile(self, share_drive_path: str, file_path: str, file) -> (int, int):
        if self.path(share_drive_path, file_path).exists():
            file.write(self.path(share_drive_path, file_path).read_bytes())
            return 0, 0

        raise OperationFailure(
            f"Failed to retrieve {file_path} on {share_drive_path}: Unable to open file",
            [],
        )

    def listPath(
        self,
        service_name: str,
        path: str,
        search: int = SMB_FILE_ATTRIBUTE_DIRECTORY,
        pattern: str = "*",
    ) -> List[SharedFile]:
        files = [
            SharedFileMock(file.name, file.is_dir())
            for file in self.path(service_name, path).glob(pattern)
            if search | SMB_FILE_ATTRIBUTE_DIRECTORY == search or file.is_file()
        ]

        if files:
            if pattern in ["", "*"]:
                files.extend([SharedFileMock(".", False), SharedFileMock("..", False)])
            # sort it for testing purposes only in order to ensure that the order is always the same
            return sorted(set(files), key=lambda file: file.filename)

        raise OperationFailure(
            f"Failed to list {path} on {service_name}: Unable to open directory", []
        )

    def echo(self, data, timeout: int = 10):
        return data

    @classmethod
    def path(cls, service_name: str, path: str) -> pathlib.Path:
        """Return the mock file path corresponding to this Remote path"""
        pathlib.Path(cls.tmpdir, "pyndows_samba_mock", service_name).mkdir(
            parents=True, exist_ok=True
        )
        if not path or path == "/":
            return pathlib.Path(cls.tmpdir, "pyndows_samba_mock", service_name)
        return pathlib.Path(cls.tmpdir, "pyndows_samba_mock", service_name, path[1:])

    @classmethod
    def add_callback(cls, method_name: str, callback: callable):
        cls.monkeypatch.setattr(cls, method_name, callback)

    @classmethod
    def cleanup(cls):
        mock_path = pathlib.Path(cls.tmpdir, "pyndows_samba_mock")
        if mock_path.exists():
            shutil.rmtree(mock_path)


@pytest.fixture
def samba_mock(monkeypatch, tmpdir) -> SMBConnectionMock:
    import smb.SMBConnection

    SMBConnectionMock.tmpdir = tmpdir
    SMBConnectionMock.monkeypatch = monkeypatch

    monkeypatch.setattr(smb.SMBConnection, "SMBConnection", SMBConnectionMock)
    import pyndows

    monkeypatch.setattr(pyndows._windows, "SMBConnection", SMBConnectionMock)

    yield SMBConnectionMock

    SMBConnectionMock.cleanup()


_date_time_for_tests = datetime.datetime(2018, 10, 11, 15, 5, 5, 663979)


class DateTimeModuleMock:
    class DateTimeMock:
        @staticmethod
        def utcnow():
            return _date_time_for_tests

    datetime = DateTimeMock


@pytest.fixture
def mock_pyndows_health_datetime(monkeypatch):
    import pyndows._windows

    monkeypatch.setattr(pyndows._windows, "datetime", DateTimeModuleMock)
