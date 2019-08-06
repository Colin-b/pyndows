import os
import os.path
import tempfile
import gzip

import pytest

import pyndows
from pyndows import samba_mock


def test_remaining_files_to_retrieve_when_reset():
    pyndows.SMBConnectionMock.files_to_retrieve["test"] = "Test"
    with pytest.raises(Exception) as exception_info:
        pyndows.SMBConnectionMock.reset()
    assert (
        str(exception_info.value)
        == "Expected files were not retrieved: {'test': 'Test'}"
    )


def test_remaining_echo_responses_when_reset():
    pyndows.SMBConnectionMock.echo_responses["test"] = "Test"
    with pytest.raises(Exception) as exception_info:
        pyndows.SMBConnectionMock.reset()
    assert str(exception_info.value) == "Echo were not requested: {'test': 'Test'}"


def test_connection_can_be_used_as_context_manager(samba_mock):
    with pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    ):
        pass


def test_non_text_file_can_be_stored(samba_mock):
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
            gzip.decompress(
                pyndows.SMBConnectionMock.stored_files[("TestShare", "TestFilePath")]
            )
            == b"Test Content Move"
        )


def test_file_retrieval_using_path(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with gzip.open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write(b"Test Content")
        pyndows.SMBConnectionMock.files_to_retrieve[
            ("TestShare", "TestFilePath")
        ] = os.path.join(temp_dir, "local_file")

        pyndows.get(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file_retrieved"),
        )
        with gzip.open(os.path.join(temp_dir, "local_file_retrieved")) as local_file:
            assert local_file.read() == b"Test Content"
