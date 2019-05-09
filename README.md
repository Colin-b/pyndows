<h2 align="center">Accessing Windows from Linux</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pyndows/job/master/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pyndows/master'></a>
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
    details = pyndows.health_details("connection identifier", machine)
```

## Embedded mock

Thanks to the embedded Samba connection mock don't need a valid connection to a distant machine to be able to write test cases.

Before declaring your test cases, mock function needs to be called to activate the mock.
```python
import pyndows

pyndows.mock()
```

You can simulate every Samba connection behavior such as:
* Exceptions being thrown
* Connectivity issue
* echo responses

And of course, the following usual operations:

### Simulate a file that can be retrieved
```python
pyndows.SMBConnectionMock.files_to_retrieve[("shared_folder_name", "/folder/file_to_retrieve")] = "File content of path to a file"
```

### Ensure the content of a file that was moved or renamed
```python
file_content = pyndows.SMBConnectionMock.stored_files[("shared_folder_name", "/folder/file_that_was_stored")]
```

### Ensure that every expected operation was performed

In the teardown method, it is expected that you call reset to ensure the state of the mock between test cases.
```python
pyndows.SMBConnectionMock.reset()
```