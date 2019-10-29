<h2 align="center">Accessing Windows from Linux</h2>

<p align="center">
<a href='https://github.tools.digital.engie.com/gempy/pyndows/releases/latest'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/pyndows/master&config=version'></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/pyndows/job/master/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/pyndows/master'></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/pyndows/job/master/cobertura/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/pyndows/master&config=testCoverage'></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/pyndows/job/master/lastSuccessfulBuild/testReport/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/pyndows/master&config=testCount'></a>
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

You can simulate every Samba connection behavior such as:
* Exceptions being thrown
* Connectivity issue
* echo responses

And of course, the following usual operations:

### Simulate a file that can be retrieved
```python
from pyndows.testing import samba_mock, SMBConnectionMock

def test_file_retrieval(samba_mock: SMBConnectionMock):
    samba_mock.files_to_retrieve[("shared_folder_name", "/folder/file_to_retrieve")] = "File content of path to a file"
```

### Ensure the content of a file that was moved or renamed
```python
from pyndows.testing import samba_mock, SMBConnectionMock

def test_file_retrieval(samba_mock: SMBConnectionMock):
    file_content = samba_mock.stored_files[("shared_folder_name", "/folder/file_that_was_stored")]
```

## How to install
1. [python 3.6+](https://www.python.org/downloads/) must be installed
2. Use pip to install module:
```sh
python -m pip install pyndows -i https://all-team-remote:tBa%40W%29tvB%5E%3C%3B2Jm3@artifactory.tools.digital.engie.com/artifactory/api/pypi/all-team-pypi-prod/simple
```
