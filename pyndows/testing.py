import os.path
import re
from typing import List, Union
from collections import namedtuple
import datetime

import pytest

from smb.smb_structs import (
    OperationFailure,
    SMB_FILE_ATTRIBUTE_DIRECTORY,
    SMB_FILE_ATTRIBUTE_READONLY,
    SMB_FILE_ATTRIBUTE_ARCHIVE,
    SMB_FILE_ATTRIBUTE_INCL_NORMAL,
)
from smb.base import SharedFile

SharedFileMock = namedtuple("SharedFileMock", ["filename", "isDirectory"])


class _FileStore(dict):
    def try_get(self, key, timeout=1):
        """
        Wait until the key is present to return the value.

        :param timeout: Maximum amount of seconds to wait
        :raises TimeoutError: in case timeout is reached and key is still not present.
        """
        end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() <= end:
            if key in self:
                return self.get(key)
        else:
            raise TimeoutError(f"{key} could not be found within {timeout} seconds.")


class SMBConnectionMock:
    """
    Mock a Samba Connection object.
    """

    should_connect = True
    stored_files = _FileStore()
    files_to_retrieve = {}
    echo_responses = {}
    storeFile_failure = False
    rename_failure = False

    @classmethod
    def reset(cls):
        cls.should_connect = True
        cls.stored_files.clear()
        if cls.files_to_retrieve:
            files = dict(cls.files_to_retrieve)
            cls.files_to_retrieve.clear()
            raise Exception(f"Expected files were not retrieved: {files}")
        if cls.echo_responses:
            echos = dict(cls.echo_responses)
            cls.echo_responses.clear()
            raise Exception(f"Echo were not requested: {echos}")
        cls.storeFile_failure = None
        cls.rename_failure = None

    def __init__(self, user_name, password, test_name, machine_name, *args, **kwargs):
        self.remote_name = machine_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def connect(self, *args):
        if isinstance(self.should_connect, Exception):
            raise self.should_connect
        return self.should_connect

    def storeFile(self, share_drive_path: str, file_path: str, file) -> int:
        if self.storeFile_failure:
            raise OperationFailure("Mock for storeFile failure.", [])
        file_content = file.read()
        try:
            # Try to store string in order to compare it easily
            file_content = file_content.decode().replace("\r\n", "\n")
        except UnicodeDecodeError:
            pass  # Keep bytes when content is not str compatible (eg. Zip file)
        SMBConnectionMock.stored_files[(share_drive_path, file_path)] = file_content
        return 0

    def rename(
        self, share_drive_path: str, initial_file_path: str, new_file_path: str
    ) -> None:
        if self.rename_failure:
            raise OperationFailure("Mock for rename failure.", [])
        SMBConnectionMock.stored_files[
            (share_drive_path, new_file_path)
        ] = SMBConnectionMock.stored_files.pop(
            (share_drive_path, initial_file_path), None
        )

    @staticmethod
    def _is_file(path_or_content: Union[str, bytes]) -> bool:
        try:
            return os.path.isfile(path_or_content)
        except ValueError:
            # Since python 3.8, this exception is not sent anymore, False is instead return
            return False

    def retrieveFile(self, share_drive_path: str, file_path: str, file) -> (int, int):
        file_id = (share_drive_path, file_path)
        if file_id not in SMBConnectionMock.files_to_retrieve:
            retrieved_file_content = SMBConnectionMock.stored_files.get(file_id)
        else:
            retrieved_file_content = SMBConnectionMock.files_to_retrieve.pop(
                (share_drive_path, file_path), None
            )
        if retrieved_file_content is not None:
            if self._is_file(retrieved_file_content):
                with open(retrieved_file_content, mode="rb") as retrieved_file:
                    file.write(retrieved_file.read())
            else:
                try:
                    # Try to store string in order to compare it easily
                    file.write(str.encode(retrieved_file_content))
                except TypeError:
                    # Keep bytes when content is not str compatible (eg. Zip file)
                    file.write(retrieved_file_content)
            return 0, 0
        raise OperationFailure("Mock for retrieveFile failure.", [])

    def listPath(
        self, service_name: str, path: str, search: int = 0, pattern: str = "*",
    ) -> List[SharedFile]:
        pattern = pattern.replace("*", ".*")
        pattern = pattern.replace("?", ".")
        service_name = service_name.replace("/", os.sep).replace("\\", os.sep)
        path = path.replace("/", os.sep).replace("\\", os.sep)
        path = path if not path or path.endswith(os.sep) else f"{path}{os.sep}"

        def to_file_in_path(file_path: str, path: str) -> (str, bool):
            if f"{os.path.dirname(file_path)}{os.sep}".startswith(path):
                file_path = file_path[len(path) :]
                return file_path.split(os.sep, maxsplit=1)[0], os.sep in file_path
            return None, None

        files_list = []
        for shared_folder, file_path in SMBConnectionMock.stored_files:
            shared_folder = shared_folder.replace("/", os.sep).replace("\\", os.sep)
            file_path = file_path.replace("/", os.sep).replace("\\", os.sep)
            file_name, is_directory = to_file_in_path(file_path, path)
            if (
                file_name
                and shared_folder == service_name
                and re.search(pattern, file_name)
            ):
                if search | SMB_FILE_ATTRIBUTE_DIRECTORY == search or not is_directory:
                    files_list.append(SharedFileMock(file_name, is_directory))

        if not files_list:
            raise OperationFailure("Mock for listPath failure.", [])
        return sorted(set(files_list), key=lambda file: file.filename)

    def echo(self, data, timeout: int = 10):
        echo_response = SMBConnectionMock.echo_responses.pop(data, None)
        if echo_response is None:
            raise OperationFailure("Mock for echo failure.", [])
        return echo_response


@pytest.fixture
def samba_mock(monkeypatch) -> SMBConnectionMock:
    import smb.SMBConnection

    monkeypatch.setattr(smb.SMBConnection, "SMBConnection", SMBConnectionMock)
    import pyndows

    monkeypatch.setattr(pyndows._windows, "SMBConnection", SMBConnectionMock)

    yield SMBConnectionMock

    SMBConnectionMock.reset()
