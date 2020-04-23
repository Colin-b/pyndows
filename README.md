<h2 align="center">Accessing Windows from Linux</h2>

<p align="center">
<a href="https://pypi.org/project/pyndows/"><img alt="pypi version" src="https://img.shields.io/pypi/v/pyndows"></a>
<a href="https://travis-ci.com/Colin-b/pyndows"><img alt="Build status" src="https://api.travis-ci.com/Colin-b/pyndows.svg?branch=master"></a>
<a href="https://travis-ci.com/Colin-b/pyndows"><img alt="Coverage" src="https://img.shields.io/badge/coverage-100%25-brightgreen"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://travis-ci.com/Colin-b/pyndows"><img alt="Number of tests" src="https://img.shields.io/badge/tests-41 passed-blue"></a>
<a href="https://pypi.org/project/pyndows/"><img alt="Number of downloads" src="https://img.shields.io/pypi/dm/pyndows"></a>
</p>

## Retrieve a file (from Windows to Linux)

```python
import pyndows

path_to_retrieved_file = ""
with pyndows.connect(...) as machine:
    pyndows.get(machine, "shared_folder_name", "/folder/requested_file_name", path_to_retrieved_file)
```

## Retrieve a file description (from Windows to Linux)

```python
import pyndows

with pyndows.connect(...) as machine:
    description = pyndows.get_file_desc(machine, "shared_folder_name", "/folder/requested_file_name")
```

## Move a file (from Linux to Windows)

```python
import pyndows

file_to_move_path = ""
with pyndows.connect(...) as machine:
    pyndows.move(machine, "shared_folder_name", "/folder/destination_file_name", file_to_move_path)
```

Note that folders will be created if not existing.

You can also provide a custom suffix for the temporary file (.tmp is used by default) via the temp_file_suffix parameter.

## Rename a file

```python
import pyndows

with pyndows.connect(...) as machine:
    pyndows.rename(machine, "shared_folder_name", "/folder/previous_file_name", "/folder/new_file_name")
```

## Ensure connectivity

```python
import pyndows

with pyndows.connect(...) as machine:
    details = pyndows.check("connection identifier", machine)
```

## Testing

You can mock remote connections by using `samba_mock` `pytest` fixture.

2 convenience methods are available:

1. `samba_mock.path(share_folder_name, file_or_folder_path)` returns a `pathlib.Path` instance that you can use as a replacement for the file on the remote connection.
    * Use `write_*()` to set the content of a file.
    * Use `read_*()` to check the content of a file.
2. `samba_mock.add_callback(method_name, callback)` provides the ability to override the mock default behavior and can be used to send custom exceptions.

Below are a few example of what can be done:

### Simulate a file that can be retrieved

```python
from pyndows.testing import samba_mock, SMBConnectionMock

def test_file_retrieval(samba_mock: SMBConnectionMock):
    samba_mock.path("shared_folder_name", "/folder/file_to_retrieve").write_text("File content of path to a file")
    # TODO Execute code relying on this file
```

### Ensure the content of a file that was moved or renamed

```python
from pyndows.testing import samba_mock, SMBConnectionMock

def test_file_retrieval(samba_mock: SMBConnectionMock):
    # TODO Execute code writing this file
    file_content = samba_mock.path("shared_folder_name", "/folder/file_that_was_stored").read_text()
```

### Simulate echo failure

```python
from smb.smb_structs import OperationFailure
from pyndows.testing import samba_mock, SMBConnectionMock

def test_file_retrieval(samba_mock: SMBConnectionMock):
    def raise_exception(*args):
        raise OperationFailure("Mock for echo failure.", [])

    samba_mock.add_callback("echo", raise_exception)
    # TODO Execute code calling echo
```

## How to install
1. [python 3.6+](https://www.python.org/downloads/) must be installed
2. Use pip to install module:
```sh
python -m pip install pyndows
```
