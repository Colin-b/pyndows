import os
import os.path

import pytest
from smb.base import SMBTimeout
from smb.smb_structs import OperationFailure

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
    samba_mock.add_callback("connect", lambda *args: False)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == r"Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_connection_timeout(samba_mock: SMBConnectionMock):
    def raise_failure(*args):
        raise TimeoutError()

    samba_mock.add_callback("connect", raise_failure)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
    assert (
        str(exception_info.value)
        == r"Impossible to connect to TestComputer (127.0.0.1:80), check connectivity or TestDomain\TestUser rights."
    )


def test_file_retrieval(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.path("TestShare", "/TestFilePath").write_text("Test Content")

    pyndows.get(
        connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
    )
    with open(os.path.join(tmpdir, "local_file")) as local_file:
        assert local_file.read() == "Test Content"


def test_operation_failure_during_file_retrieval(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.get(
            connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
        )
    assert (
        str(exception_info.value)
        == r"Unable to retrieve \\TestComputer\TestShare/TestFilePath file"
    )


def test_file_move(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    pyndows.move(
        connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
    )

    assert (
        samba_mock.path("TestShare", "/TestFilePath").read_text() == "Test Content Move"
    )


def test_file_move_with_folder_creation(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    pyndows.move(
        connection,
        "TestShare",
        "/Folder1/Folder2/Folder3/TestFilePath",
        os.path.join(tmpdir, "local_file"),
    )

    assert (
        samba_mock.path(
            "TestShare", "/Folder1/Folder2/Folder3/TestFilePath"
        ).read_text()
        == "Test Content Move"
    )


def test_file_move_with_last_folder_creation(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    samba_mock.path("TestShare", "/Folder1/Folder2").mkdir(parents=True)
    pyndows.move(
        connection,
        "TestShare",
        "/Folder1/Folder2/Folder3/TestFilePath",
        os.path.join(tmpdir, "local_file"),
    )

    assert (
        samba_mock.path(
            "TestShare", "/Folder1/Folder2/Folder3/TestFilePath"
        ).read_text()
        == "Test Content Move"
    )


def test_file_move_with_last_folder_creation_failure(
    samba_mock: SMBConnectionMock, tmpdir
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    samba_mock.path("TestShare", "/Folder1/Folder2").mkdir(parents=True)

    def raise_failure(*args):
        raise OperationFailure("Unable to create directory", [])

    samba_mock.add_callback("createDirectory", raise_failure)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.move(
            connection,
            "TestShare",
            "/Folder1/Folder2/Folder3/TestFilePath",
            os.path.join(tmpdir, "local_file"),
        )

    assert (
        str(exception_info.value)
        == r"Unable to write \\TestComputer\TestShare/Folder1/Folder2/Folder3/TestFilePath.tmp"
    )


def test_store_file_operation_failure_during_file_move(
    samba_mock: SMBConnectionMock, tmpdir
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    def raise_failure(*args):
        raise OperationFailure("Mock for storeFile failure.", [])

    samba_mock.add_callback("storeFile", raise_failure)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.move(
            connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
        )

    assert (
        str(exception_info.value)
        == r"Unable to write \\TestComputer\TestShare/TestFilePath.tmp"
    )


def test_smbtimeout_failure_during_storefile(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    def raise_failure(*args):
        raise SMBTimeout()

    samba_mock.add_callback("storeFile", raise_failure)
    with pytest.raises(SMBTimeout):
        pyndows.move(
            connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
        )


def test_rename_operation_failure_during_file_move(
    samba_mock: SMBConnectionMock, tmpdir
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write("Test Content Move")

    def raise_failure(*args):
        raise OperationFailure("Mock for rename failure.", [])

    samba_mock.add_callback("rename", raise_failure)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.move(
            connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
        )

    assert (
        str(exception_info.value)
        == r"Unable to rename temp file into \\TestComputer\TestShare/TestFilePath"
    )


def test_file_rename(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/file_to_rename").write_text("Test Rename")

    pyndows.rename(connection, "TestShare", "/file_to_rename", "/file_new_name")

    assert not samba_mock.path("TestShare", "/file_to_rename").exists()
    assert samba_mock.path("TestShare", "/file_new_name").read_text() == "Test Rename"


def test_rename_operation_failure_during_file_rename(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/file_to_rename").write_text("Test Rename")

    def raise_failure(*args):
        raise OperationFailure("Mock for rename failure.", [])

    samba_mock.add_callback("rename", raise_failure)
    with pytest.raises(pyndows.PyndowsException) as exception_info:
        pyndows.rename(connection, "TestShare", "/file_to_rename", "/file_new_name")

    assert (
        str(exception_info.value)
        == r"Unable to rename \\TestComputer\TestShare/file_to_rename into \\TestComputer\TestShare/file_new_name"
    )


def test_file_rename_file_does_not_exist(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    with pytest.raises(FileNotFoundError) as exception_info:
        pyndows.rename(connection, "TestShare", "/file_to_rename_2", "/file_new_name")

    assert (
        str(exception_info.value)
        == r"\\TestComputer\TestShare/file_to_rename_2 doesn't exist"
    )


def test_get_all_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A").mkdir()
    samba_mock.path("TestShare", "/A/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/2").write_text("Test Find")
    samba_mock.path("TestShare", "/A/3").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i").mkdir()
    samba_mock.path("TestShare", "/A/i/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i/2").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/A"
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="3", isDirectory=False),
        SharedFileMock(filename="i", isDirectory=True),
    ]


def test_get_all_sub_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A").mkdir()
    samba_mock.path("TestShare", "/A/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/2").write_text("Test Find")
    samba_mock.path("TestShare", "/A/3").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i").mkdir()
    samba_mock.path("TestShare", "/A/i/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i/2").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/A/i"
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
    ]


def test_get_all_folder_contents_empty_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/A"
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_empty_shared_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path=""
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_non_existing_folder(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/B"
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_non_existing_shared_folder(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "AnotherTestShare", folder_path=""
    )

    assert shared_folder_contents == []


def test_get_all_folder_contents_excluding_directories(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A").mkdir()
    samba_mock.path("TestShare", "/A/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/2").write_text("Test Find")
    samba_mock.path("TestShare", "/A/3").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i").mkdir()
    samba_mock.path("TestShare", "/A/i/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i/2").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/A", include_folders=False
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="2", isDirectory=False),
        SharedFileMock(filename="3", isDirectory=False),
    ]


def test_get_all_folder_contents_matching_a_pattern(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A").mkdir()
    samba_mock.path("TestShare", "/A/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/12").write_text("Test Find")
    samba_mock.path("TestShare", "/A/3").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i").mkdir()
    samba_mock.path("TestShare", "/A/i/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/1i").mkdir()
    samba_mock.path("TestShare", "/A/1i/2").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path="/A", pattern="1*"
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="12", isDirectory=False),
        SharedFileMock(filename="1i", isDirectory=True),
    ]


def test_get_all_folder_contents_matching_a_pattern_with_question_mark_wildcard(
    samba_mock: SMBConnectionMock,
):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/test_12345_test").write_text("Test Find")
    samba_mock.path("TestShare", "/test_123456_test").write_text("Test Find")
    samba_mock.path("TestShare", "/test_123_test").write_text("Test Find")
    samba_mock.path("TestShare", "/test_1234M_test").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", pattern="test_?????_test"
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="test_12345_test", isDirectory=False),
        SharedFileMock(filename="test_1234M_test", isDirectory=False),
    ]


def test_get_all_shared_folder_contents(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A").mkdir()
    samba_mock.path("TestShare", "/A/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/2").write_text("Test Find")
    samba_mock.path("TestShare", "/A/3").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i").mkdir()
    samba_mock.path("TestShare", "/A/i/1").write_text("Test Find")
    samba_mock.path("TestShare", "/A/i/2").write_text("Test Find")

    shared_folder_contents = pyndows.get_folder_content(
        connection, "TestShare", folder_path=""
    )

    assert shared_folder_contents == [
        SharedFileMock(filename="1", isDirectory=False),
        SharedFileMock(filename="A", isDirectory=True),
    ]


def test_get_file_desc_file_exists(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/file_to_find").write_text("Test Find")

    file = pyndows.get_file_desc(connection, "TestShare", "/file_to_find")

    assert file.filename == "file_to_find"


def test_get_file_desc_file_does_not_exist(samba_mock: SMBConnectionMock):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )

    samba_mock.path("TestShare", "/file_to_find").write_text("Test Find")

    assert pyndows.get_file_desc(connection, "TestShare", "/non_existing") is None
