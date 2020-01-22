import os
import os.path
import tempfile
import gzip

import pytest

import pyndows
from pyndows.testing import samba_mock, SMBConnectionMock


def test_remaining_files_to_retrieve_when_reset():
    pyndows.testing.SMBConnectionMock.files_to_retrieve["tests"] = "Test"
    with pytest.raises(Exception) as exception_info:
        pyndows.testing.SMBConnectionMock.reset()
    assert (
        str(exception_info.value)
        == "Expected files were not retrieved: {'tests': 'Test'}"
    )


def test_remaining_echo_responses_when_reset():
    pyndows.testing.SMBConnectionMock.echo_responses["tests"] = "Test"
    with pytest.raises(Exception) as exception_info:
        pyndows.testing.SMBConnectionMock.reset()
    assert str(exception_info.value) == "Echo were not requested: {'tests': 'Test'}"


def test_connection_can_be_used_as_context_manager(samba_mock: SMBConnectionMock):
    with pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    ):
        pass


def test_non_text_file_can_be_stored(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with gzip.open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write(b"Test Content Move")

        pyndows.move(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file"),
        )

        assert (
            gzip.decompress(samba_mock.stored_files[("TestShare", "TestFilePath")])
            == b"Test Content Move"
        )


def test_file_retrieval_using_path(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with gzip.open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write(b"Test Content")
        samba_mock.files_to_retrieve[("TestShare", "TestFilePath")] = os.path.join(
            temp_dir, "local_file"
        )

        pyndows.get(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file_retrieved"),
        )
        with gzip.open(os.path.join(temp_dir, "local_file_retrieved")) as local_file:
            assert local_file.read() == b"Test Content"


def test_file_retrieval_using_str_content(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        samba_mock.files_to_retrieve[("TestShare", "TestFilePath")] = "data"

        pyndows.get(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file_retrieved"),
        )
        with open(os.path.join(temp_dir, "local_file_retrieved"), "rt") as local_file:
            assert local_file.read() == "data"


def test_file_retrieval_using_bytes_content(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        bytes_content_file_path = os.path.join(temp_dir, "local_file")
        with gzip.open(bytes_content_file_path, mode="w") as distant_file:
            distant_file.write(b"Test Content")
        samba_mock.files_to_retrieve[("TestShare", "TestFilePath")] = open(
            bytes_content_file_path, "rb"
        ).read()

        pyndows.get(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file_retrieved"),
        )
        with gzip.open(os.path.join(temp_dir, "local_file_retrieved")) as local_file:
            assert local_file.read() == b"Test Content"
