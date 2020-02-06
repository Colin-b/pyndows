from datetime import datetime
import logging
import os
from typing import Optional, List

from smb.SMBConnection import (
    SMBConnection,
    SMB_FILE_ATTRIBUTE_READONLY,
    SMB_FILE_ATTRIBUTE_ARCHIVE,
    SMB_FILE_ATTRIBUTE_INCL_NORMAL,
    SMB_FILE_ATTRIBUTE_DIRECTORY,
)
from smb.base import SharedFile
from smb.smb_structs import OperationFailure

logger = logging.getLogger(__name__)


def connect(
    machine_name: str, ip: str, port: int, domain: str, user_name: str, password: str
) -> SMBConnection:
    logger.info(f"Connecting to {machine_name} ({ip}:{port})...")

    connection = SMBConnection(
        user_name,
        password,
        "testclient",
        machine_name,
        domain=domain,
        use_ntlm_v2=True,
        is_direct_tcp=True,
    )
    try:
        if not connection.connect(ip, port):
            raise Exception(
                f"Impossible to connect to {machine_name} ({ip}:{port}), "
                f"check connectivity or {domain}\\{user_name} rights."
            )
    except TimeoutError:
        raise Exception(
            f"Impossible to connect to {machine_name} ({ip}:{port}), "
            f"check connectivity or {domain}\\{user_name} rights."
        )

    logger.info(f"Connected to {machine_name} ({ip}:{port}).")
    return connection


def get(
    connection: SMBConnection, share_folder: str, file_path: str, output_file_path: str
):
    logger.info(
        f"Retrieving file \\\\{connection.remote_name}\\{share_folder}{file_path}..."
    )

    with open(output_file_path, "wb") as file:
        try:
            connection.retrieveFile(share_folder, file_path, file)
        except OperationFailure:
            raise Exception(
                f"Unable to retrieve \\\\{connection.remote_name}\\{share_folder}{file_path} file"
            )

    logger.info(
        f"File \\\\{connection.remote_name}\\{share_folder}{file_path} stored within {output_file_path}."
    )


def move(
    connection: SMBConnection,
    share_folder: str,
    file_path: str,
    input_file_path: str,
    temp_file_suffix=".tmp",
):
    logger.info(
        f"Moving {input_file_path} file to \\\\{connection.remote_name}\\{share_folder}{file_path}..."
    )

    try:
        with open(input_file_path, "rb") as input_file:
            connection.storeFile(
                share_folder, f"{file_path}{temp_file_suffix}", input_file
            )
    except OperationFailure:
        raise Exception(
            f"Unable to write \\\\{connection.remote_name}\\{share_folder}{file_path}{temp_file_suffix}"
        )

    if temp_file_suffix:
        try:
            connection.rename(share_folder, f"{file_path}{temp_file_suffix}", file_path)
        except OperationFailure:
            raise Exception(
                f"Unable to rename temp file into \\\\{connection.remote_name}\\{share_folder}{file_path}"
            )

    logger.info(f"File copied. Removing {input_file_path} file...")
    os.remove(input_file_path)

    logger.info(
        f"{input_file_path} file moved within \\\\{connection.remote_name}\\{share_folder}{file_path}."
    )


def rename(
    connection: SMBConnection, share_folder: str, old_file_path: str, new_file_path: str
):
    if get_file_desc(connection, share_folder, old_file_path):
        _rename(connection, share_folder, old_file_path, new_file_path)
    else:
        raise FileNotFoundError(
            f"\\\\{connection.remote_name}\\{share_folder}{old_file_path} doesn't exist"
        )


def _rename(
    connection: SMBConnection, share_folder: str, old_file_path: str, new_file_path: str
):
    logger.info(
        f"Renaming \\\\{connection.remote_name}\\{share_folder}{old_file_path} "
        f"into \\\\{connection.remote_name}\\{share_folder}{new_file_path}..."
    )
    try:
        connection.rename(share_folder, old_file_path, new_file_path)
        logger.info("File renamed...")
    except OperationFailure:
        raise Exception(
            f"Unable to rename \\\\{connection.remote_name}\\{share_folder}{old_file_path} "
            f"into \\\\{connection.remote_name}\\{share_folder}{new_file_path}"
        )


def get_folder_content(
    connection: SMBConnection,
    share_folder: str,
    folder_path: str = "",
    include_folders: bool = True,
    pattern: str = "*",
) -> List[SharedFile]:
    """
    Returns a list of files or folders matching given pattern within a folder (non-recursively).

    :param connection: Samba connection.
    :param share_folder: Remote computer name.
    :param folder_path: Folder path for which the content is returned.
    Must be relative to share_folder.
    Defaults to the root of the shared folder (empty string).
    :param include_folders: Should sub folders be included in the results.
    Include sub folders by default. Set to False to list only files.
    :param pattern: Filter out files or sub folders based on this pattern (`*` character means all).
    Include everything but . and .. by default (*).
    Respects the MS-CIFS protocol. https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cifs/dc92d939-ec45-40c8-96e5-4c4091e4ab43
    :return: A List of SharedFile objects, empty if the given folder does not exist.
    """
    search = (
        SMB_FILE_ATTRIBUTE_READONLY
        | SMB_FILE_ATTRIBUTE_ARCHIVE
        | SMB_FILE_ATTRIBUTE_INCL_NORMAL
    )
    if include_folders:
        search = search | SMB_FILE_ATTRIBUTE_DIRECTORY
    logger.info(
        f"Listing the content of \\\\{connection.remote_name}\\{share_folder}\\{folder_path} ..."
    )
    try:
        return [
            file
            for file in connection.listPath(
                share_folder, folder_path, pattern=pattern, search=search
            )
            if file.filename not in (".", "..")
        ]
    except OperationFailure:
        return []


def get_file_desc(
    connection: SMBConnection, share_folder: str, file_path: str
) -> Optional[SharedFile]:
    """
    :return: None if file do not exists, Samba file description if it does.
    """
    logger.info(
        f"Returning \\\\{connection.remote_name}\\{share_folder}{file_path} description..."
    )
    try:
        files = connection.listPath(
            share_folder,
            os.path.dirname(file_path),
            pattern=os.path.basename(file_path),
        )
        return files[0] if files else None
    except OperationFailure:
        return


def check(computer_name: str, connection: SMBConnection) -> (str, dict):
    """
    Return Health check for a Samba connection.

    :param computer_name: Remote computer name.
    :param connection: Samba connection.
    :return: A tuple with a string providing the status (pass, warn, fail) and the checks.
    Checks are based on https://inadarei.github.io/rfc-healthcheck/
    """
    try:
        response = connection.echo(b"")
        return (
            "pass",
            {
                f"{computer_name}:echo": {
                    "componentType": connection.remote_name,
                    "observedValue": response.decode(),
                    "status": "pass",
                    "time": datetime.utcnow().isoformat(),
                }
            },
        )
    except Exception as e:
        return (
            "fail",
            {
                f"{computer_name}:echo": {
                    "componentType": connection.remote_name,
                    "status": "fail",
                    "time": datetime.utcnow().isoformat(),
                    "output": str(e),
                }
            },
        )
