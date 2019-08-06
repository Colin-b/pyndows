import os
import os.path
import tempfile

import pytest

import pyndows
from pyndows import samba_mock


def test_successful_connection(samba_mock):
    assert (
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        is not None
    )


def test_connection_failure(samba_mock):
    samba_mock.should_connect = False
    with pytest.raises(Exception) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == "Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_connection_timeout(samba_mock):
    samba_mock.should_connect = TimeoutError()
    with pytest.raises(Exception) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == "Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_file_retrieval(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        samba_mock.files_to_retrieve[("TestShare", "TestFilePath")] = "Test Content"

        pyndows.get(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file"),
        )
        with open(os.path.join(temp_dir, "local_file")) as local_file:
            assert local_file.read() == "Test Content"


def test_operation_failure_during_file_retrieval(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(Exception) as exception_info:
            pyndows.get(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )
        assert (
            str(exception_info.value)
            == r"Unable to retrieve \\TestComputer\TestShareTestFilePath file"
        )


def test_file_move(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write("Test Content Move")

        pyndows.move(
            connection,
            "TestShare",
            "TestFilePath",
            os.path.join(temp_dir, "local_file"),
        )

        assert (
            samba_mock.stored_files[("TestShare", "TestFilePath")]
            == "Test Content Move"
        )


def test_storeFile_operation_failure_during_file_move(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write("Test Content Move")

        samba_mock.storeFile_failure = True
        with pytest.raises(Exception) as exception_info:
            pyndows.move(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )

        assert (
            str(exception_info.value)
            == r"Unable to write \\TestComputer\TestShareTestFilePath.tmp"
        )


def test_rename_operation_failure_during_file_move(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
            distant_file.write("Test Content Move")

        samba_mock.rename_failure = True
        with pytest.raises(Exception) as exception_info:
            pyndows.move(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )

        assert (
            str(exception_info.value)
            == r"Unable to rename temp file into \\TestComputer\TestShareTestFilePath"
        )


def test_file_rename(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_rename")] = "Test Rename"

    pyndows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

    assert ("TestShare/", "file_to_rename") not in samba_mock.stored_files
    assert samba_mock.stored_files[("TestShare/", "file_new_name")] == "Test Rename"


def test_rename_operation_failure_during_file_rename(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_rename")] = "Test Rename"

    samba_mock.rename_failure = True
    with pytest.raises(Exception) as exception_info:
        pyndows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

    assert (
        str(exception_info.value)
        == r"Unable to rename \\TestComputer\TestShare/file_to_rename into \\TestComputer\TestShare/file_new_name"
    )


def test_file_rename_file_does_not_exist(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    with pytest.raises(FileNotFoundError) as exception_info:
        pyndows.rename(connection, "TestShare\\", "file_to_rename_2", "file_new_name")

    assert (
        str(exception_info.value)
        == r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist"
    )


def test_get_file_desc_file_exists(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_find")] = "Test Find"

    founded_file = pyndows.get_file_desc(connection, "TestShare/", "file_to_find")

    assert founded_file.filename == "file_to_find"


def test_get_file_desc_file_does_not_exist(samba_mock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_find")] = "Test Find"

    founded_file = pyndows.get_file_desc(
        connection, "TestShare/", "nonexistent_file_to_find"
    )

    assert founded_file is None
