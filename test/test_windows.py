import logging
import os
import os.path
import tempfile
import unittest
import unittest.mock as mock
import gzip

import pyndows

pyndows.mock()

logger = logging.getLogger(__name__)


class WindowsTest(unittest.TestCase):
    def setUp(self):
        logger.info(f"-------------------------------")
        logger.info(f"Start of {self._testMethodName}")

    def tearDown(self):
        pyndows.SMBConnectionMock.reset()
        logger.info(f"End of {self._testMethodName}")
        logger.info(f"-------------------------------")

    def test_successful_connection(self):
        self.assertIsNotNone(
            pyndows.connect(
                "TestComputer",
                "127.0.0.1",
                80,
                "TestDomain",
                "TestUser",
                "TestPassword",
            )
        )

    def test_connection_failure(self):
        pyndows.SMBConnectionMock.should_connect = False
        with self.assertRaises(Exception) as cm:
            pyndows.connect(
                "TestComputer",
                "127.0.0.1",
                80,
                "TestDomain",
                "TestUser",
                "TestPassword",
            )
        self.assertEqual(
            "Impossible to connect to TestComputer (127.0.0.1:80), "
            "check connectivity or TestDomain\TestUser rights.",
            str(cm.exception),
        )

    def test_connection_timeout(self):
        pyndows.SMBConnectionMock.should_connect = TimeoutError()
        with self.assertRaises(Exception) as cm:
            pyndows.connect(
                "TestComputer",
                "127.0.0.1",
                80,
                "TestDomain",
                "TestUser",
                "TestPassword",
            )
        self.assertEqual(
            "Impossible to connect to TestComputer (127.0.0.1:80), "
            "check connectivity or TestDomain\TestUser rights.",
            str(cm.exception),
        )

    def test_file_retrieval(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            pyndows.SMBConnectionMock.files_to_retrieve[
                ("TestShare", "TestFilePath")
            ] = "Test Content"

            pyndows.get(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )
            with open(os.path.join(temp_dir, "local_file")) as local_file:
                self.assertEqual(local_file.read(), "Test Content")

    def test_operation_failure_during_file_retrieval(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(Exception) as cm:
                pyndows.get(
                    connection,
                    "TestShare",
                    "TestFilePath",
                    os.path.join(temp_dir, "local_file"),
                )
            self.assertEqual(
                r"Unable to retrieve \\TestComputer\TestShareTestFilePath file",
                str(cm.exception),
            )

    def test_file_move(self):
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

            self.assertEqual(
                pyndows.SMBConnectionMock.stored_files[("TestShare", "TestFilePath")],
                "Test Content Move",
            )

    def test_storeFile_operation_failure_during_file_move(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
                distant_file.write("Test Content Move")

            pyndows.SMBConnectionMock.storeFile_failure = True
            with self.assertRaises(Exception) as cm:
                pyndows.move(
                    connection,
                    "TestShare",
                    "TestFilePath",
                    os.path.join(temp_dir, "local_file"),
                )

            self.assertEqual(
                r"Unable to write \\TestComputer\TestShareTestFilePath.tmp",
                str(cm.exception),
            )

    def test_rename_operation_failure_during_file_move(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
                distant_file.write("Test Content Move")

            pyndows.SMBConnectionMock.rename_failure = True
            with self.assertRaises(Exception) as cm:
                pyndows.move(
                    connection,
                    "TestShare",
                    "TestFilePath",
                    os.path.join(temp_dir, "local_file"),
                )

            self.assertEqual(
                r"Unable to rename temp file into \\TestComputer\TestShareTestFilePath",
                str(cm.exception),
            )

    def test_file_rename(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        pyndows.SMBConnectionMock.stored_files[
            ("TestShare/", "file_to_rename")
        ] = "Test Rename"

        pyndows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

        self.assertNotIn(
            ("TestShare/", "file_to_rename"), pyndows.SMBConnectionMock.stored_files
        )
        self.assertEqual(
            pyndows.SMBConnectionMock.stored_files[("TestShare/", "file_new_name")],
            "Test Rename",
        )

    def test_rename_operation_failure_during_file_rename(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        pyndows.SMBConnectionMock.stored_files[
            ("TestShare/", "file_to_rename")
        ] = "Test Rename"

        pyndows.SMBConnectionMock.rename_failure = True
        with self.assertRaises(Exception) as cm:
            pyndows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

        self.assertEqual(
            r"Unable to rename \\TestComputer\TestShare/file_to_rename into \\TestComputer\TestShare/file_new_name",
            str(cm.exception),
        )

    def test_file_rename_file_does_not_exist(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        with self.assertRaises(FileNotFoundError) as cm:
            pyndows.rename(
                connection, "TestShare\\", "file_to_rename_2", "file_new_name"
            )

        self.assertEqual(
            str(cm.exception),
            r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist",
        )

    def test_get_file_desc_file_exists(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        pyndows.SMBConnectionMock.stored_files[
            ("TestShare/", "file_to_find")
        ] = "Test Find"

        founded_file = pyndows.get_file_desc(connection, "TestShare/", "file_to_find")

        self.assertEqual(founded_file.filename, "file_to_find")

    def test_get_file_desc_file_does_not_exist(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        pyndows.SMBConnectionMock.stored_files[
            ("TestShare/", "file_to_find")
        ] = "Test Find"

        founded_file = pyndows.get_file_desc(
            connection, "TestShare/", "nonexistent_file_to_find"
        )

        self.assertIsNone(founded_file)


class SambaMockTest(unittest.TestCase):
    def test_remaining_files_to_retrieve_when_reset(self):
        pyndows.SMBConnectionMock.files_to_retrieve["test"] = "Test"
        with self.assertRaises(Exception) as cm:
            pyndows.SMBConnectionMock.reset()
        self.assertEqual(
            str(cm.exception), "Expected files were not retrieved: {'test': 'Test'}"
        )

    def test_remaining_echo_responses_when_reset(self):
        pyndows.SMBConnectionMock.echo_responses["test"] = "Test"
        with self.assertRaises(Exception) as cm:
            pyndows.SMBConnectionMock.reset()
        self.assertEqual(str(cm.exception), "Echo were not requested: {'test': 'Test'}")

    def test_connection_can_be_used_as_context_manager(self):
        with pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        ):
            self.assertTrue(True)

    def test_non_text_file_can_be_stored(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with gzip.open(
                os.path.join(temp_dir, "local_file"), mode="w"
            ) as distant_file:
                distant_file.write(b"Test Content Move")

            pyndows.move(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )

            self.assertEqual(
                gzip.decompress(
                    pyndows.SMBConnectionMock.stored_files[
                        ("TestShare", "TestFilePath")
                    ]
                ),
                b"Test Content Move",
            )

    def test_file_retrieval_using_path(self):
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with gzip.open(
                os.path.join(temp_dir, "local_file"), mode="w"
            ) as distant_file:
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
            with gzip.open(
                os.path.join(temp_dir, "local_file_retrieved")
            ) as local_file:
                self.assertEqual(local_file.read(), b"Test Content")


class WindowsHealthTest(unittest.TestCase):
    class UTCDateTimeMock:
        @staticmethod
        def isoformat():
            return "2018-10-11T15:05:05.663979"

    def setUp(self):
        logger.info(f"-------------------------------")
        logger.info(f"Start of {self._testMethodName}")

    def tearDown(self):
        pyndows.SMBConnectionMock.reset()
        logger.info(f"End of {self._testMethodName}")
        logger.info(f"-------------------------------")

    @mock.patch("pyndows._windows.datetime")
    def test_pass_health_check(self, datetime_mock):
        datetime_mock.utcnow = mock.Mock(return_value=self.UTCDateTimeMock)
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        pyndows.SMBConnectionMock.echo_responses[b""] = b""
        self.assertEqual(
            (
                "pass",
                {
                    "test:echo": {
                        "componentType": "TestComputer",
                        "observedValue": "",
                        "status": "pass",
                        "time": "2018-10-11T15:05:05.663979",
                    }
                },
            ),
            pyndows.health_details("test", connection),
        )

    @mock.patch("pyndows._windows.datetime")
    def test_fail_health_check(self, datetime_mock):
        datetime_mock.utcnow = mock.Mock(return_value=self.UTCDateTimeMock)
        connection = pyndows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        self.assertEqual(
            (
                "fail",
                {
                    "test:echo": {
                        "componentType": "TestComputer",
                        "status": "fail",
                        "time": "2018-10-11T15:05:05.663979",
                        "output": f"Mock for echo failure.{os.linesep}",
                    }
                },
            ),
            pyndows.health_details("test", connection),
        )


if __name__ == "__main__":
    unittest.main()
