import os
import os.path
import gzip
import threading
import time

import pytest

import pyndows
from pyndows.testing import samba_mock, SMBConnectionMock, try_get


def test_connection_can_be_used_as_context_manager(samba_mock: SMBConnectionMock):
    with pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    ):
        assert True


def test_non_text_file_can_be_stored(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with gzip.open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write(b"Test Content Move")

    pyndows.move(
        connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
    )

    assert (
        gzip.decompress(samba_mock.path("TestShare", "/TestFilePath").read_bytes())
        == b"Test Content Move"
    )


def test_async_retrieval(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with gzip.open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write(b"Test Content Move")

    def add_with_delay(delay: int):
        time.sleep(delay)
        pyndows.move(
            connection,
            "TestShare",
            "/TestFilePath",
            os.path.join(tmpdir, "local_file"),
            write_to_new_folder_after=0,
        )

    thread = threading.Thread(target=add_with_delay, args=(2,))
    thread.start()

    retrieved_file = try_get(samba_mock.path("TestShare", "/TestFilePath"), timeout=4)
    thread.join()
    assert gzip.decompress(retrieved_file.read_bytes()) == b"Test Content Move"


def test_async_retrieval_timeout(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with gzip.open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write(b"Test Content Move")

    def add_with_delay(delay: int):
        time.sleep(delay)
        pyndows.move(
            connection,
            "TestShare",
            "/TestFilePath",
            os.path.join(tmpdir, "local_file"),
            write_to_new_folder_after=0,
        )

    thread = threading.Thread(target=add_with_delay, args=(2,))
    thread.start()

    with pytest.raises(TimeoutError) as exception_info:
        try_get(samba_mock.path("TestShare", "/TestFilePath"))
    thread.join()
    assert (
        str(exception_info.value) == "TestFilePath could not be found within 1 seconds."
    )


def test_file_retrieval_using_path(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.path("TestShare", "/TestFilePath").write_bytes(
        gzip.compress(b"Test Content")
    )

    pyndows.get(
        connection,
        "TestShare",
        "/TestFilePath",
        os.path.join(tmpdir, "local_file_retrieved"),
    )
    with gzip.open(os.path.join(tmpdir, "local_file_retrieved")) as local_file:
        assert local_file.read() == b"Test Content"


def test_file_retrieval_using_str_content(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.path("TestShare", "/TestFilePath").write_text("data")

    pyndows.get(
        connection,
        "TestShare",
        "/TestFilePath",
        os.path.join(tmpdir, "local_file_retrieved"),
    )
    with open(os.path.join(tmpdir, "local_file_retrieved"), "rt") as local_file:
        assert local_file.read() == "data"


def test_file_retrieval_using_bytes_content(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    samba_mock.path("TestShare", "/TestFilePath").write_bytes(
        gzip.compress(b"Test Content")
    )

    pyndows.get(
        connection,
        "TestShare",
        "/TestFilePath",
        os.path.join(tmpdir, "local_file_retrieved"),
    )
    with gzip.open(os.path.join(tmpdir, "local_file_retrieved")) as local_file:
        assert local_file.read() == b"Test Content"


def test_retrieval_of_stored_non_text_file(samba_mock: SMBConnectionMock, tmpdir):
    connection = pyndows.connect(
        "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
    )
    with gzip.open(os.path.join(tmpdir, "local_file"), mode="w") as distant_file:
        distant_file.write(b"Test Content Move")

    pyndows.move(
        connection, "TestShare", "/TestFilePath", os.path.join(tmpdir, "local_file")
    )

    pyndows.get(
        connection,
        "TestShare",
        "/TestFilePath",
        os.path.join(tmpdir, "local_file_retrieved"),
    )

    with gzip.open(os.path.join(tmpdir, "local_file_retrieved")) as local_file:
        assert local_file.read() == b"Test Content Move"

    assert (
        gzip.decompress(samba_mock.path("TestShare", "/TestFilePath").read_bytes())
        == b"Test Content Move"
    )
