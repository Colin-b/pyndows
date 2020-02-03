import os
import os.path
import tempfile

import pytest

import pyndows
from pyndows.testing import samba_mock, SMBConnectionMock, SharedFileMock


def test_successful_connection(samba_mock: SMBConnectionMock):
    assert (
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        is not None
    )


def test_connection_failure(samba_mock: SMBConnectionMock):
    samba_mock.should_connect = False
    with pytest.raises(Exception) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == r"Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_connection_timeout(samba_mock: SMBConnectionMock):
    samba_mock.should_connect = TimeoutError()
    with pytest.raises(Exception) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == r"Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_file_retrieval(samba_mock: SMBConnectionMock):
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


def test_operation_failure_during_file_retrieval(samba_mock: SMBConnectionMock):
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


def test_file_move(samba_mock: SMBConnectionMock):
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


def test_store_file_operation_failure_during_file_move(samba_mock: SMBConnectionMock):
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


def test_rename_operation_failure_during_file_move(samba_mock: SMBConnectionMock):
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


def test_file_rename(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_rename")] = "Test Rename"

    pyndows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

    assert ("TestShare/", "file_to_rename") not in samba_mock.stored_files
    assert samba_mock.stored_files[("TestShare/", "file_new_name")] == "Test Rename"


def test_rename_operation_failure_during_file_rename(samba_mock: SMBConnectionMock):
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


def test_file_rename_file_does_not_exist(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    with pytest.raises(FileNotFoundError) as exception_info:
        pyndows.rename(connection, "TestShare\\", "file_to_rename_2", "file_new_name")

    assert (
        str(exception_info.value)
        == r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist"
    )


def test_get_all_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare/", "A/2"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i/1"): "Test Find",
            ("TestShare/", "A/i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A"
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="3", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="i", isDirectory=True),
    }


def test_get_all_folder_contents_providing_paths_with_backslashes(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare\\", "1"): "Test Find",
            ("TestShare\\", "A\\1"): "Test Find",
            ("TestShare\\", "A\\2"): "Test Find",
            ("TestShare\\", "A\\3"): "Test Find",
            ("TestShare\\", "A\\i\\1"): "Test Find",
            ("TestShare\\", "A\\i\\2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare\\", folder_path="A"
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="3", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="i", isDirectory=True),
    }


def test_get_all_sub_folder_contents_providing_paths_with_a_mix_of_slashes_and_backslashes(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare\\", "A/2"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i\\1"): "Test Find",
            ("TestShare\\", "A/i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A\\i"
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
    }


def test_get_all_folder_contents_empty_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "1")] = "Test Find"

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A"
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_empty_shared_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path=""
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_non_existing_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="B"
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_non_existing_shared_folder(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "1")] = "Test Find"

    shared_folder_contents = pyndows.get_folder_content(
        connection, "AnotherTestShare/", folder_path=""
    )

    assert shared_folder_contents == []


def test_get_all_folder_removes_self_directory_and_parent_directory(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {("TestShare/", "."): "Test Find", ("TestShare/", ".."): "Test Find",}
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path=""
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_excluding_directories(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare/", "A/2"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i/1"): "Test Find",
            ("TestShare/", "A/i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A", include_folders=False
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="3", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
    }


def test_get_all_folder_contents_matching_a_pattern(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare/", "A/12"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i/1"): "Test Find",
            ("TestShare/", "A/1i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A", pattern="^1"
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="12", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="1i", isDirectory=True),
    }


def test_get_all_shared_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare/", "A/2"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i/1"): "Test Find",
            ("TestShare/", "A/i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path=""
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="A", isDirectory=True),
        SharedFileMock(filename="1", isDirectory=False),
    }


def test_get_all_sub_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files.update(
        {
            ("TestShare/", "1"): "Test Find",
            ("TestShare/", "A/1"): "Test Find",
            ("TestShare/", "A/2"): "Test Find",
            ("TestShare/", "A/3"): "Test Find",
            ("TestShare/", "A/i/1"): "Test Find",
            ("TestShare/", "A/i/2"): "Test Find",
        }
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare/", folder_path="A/i"
    )

    assert set(shared_folder_contents) == {
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="1", isDirectory=False),
    }


def test_get_file_desc_file_exists(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_find")] = "Test Find"

    founded_file = pyndows.get_file_desc(connection, "TestShare/", "file_to_find")

    assert founded_file.filename == "file_to_find"


def test_get_file_desc_file_does_not_exist(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.stored_files[("TestShare/", "file_to_find")] = "Test Find"

    founded_file = pyndows.get_file_desc(
        connection, "TestShare/", "nonexistent_file_to_find"
    )

    assert founded_file is None
