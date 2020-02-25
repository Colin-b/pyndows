# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.4.0] - 2020-02-25
### Added
- `timeout` parameter for `pyndows.move`.
- `SMBConnectionMock.storeFile_exceptions` to raise exception in case storeFile is called.

### Deprecated
- `SMBConnectionMock.storeFile_failure`, use `SMBConnectionMock.storeFile_exceptions` instead.

## [3.3.1] - 2020-02-06
### Fixed
- Mock now replaces the `?` wildcard defined in [MS-CIFS protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cifs/dc92d939-ec45-40c8-96e5-4c4091e4ab43) by a `.`.

## [3.3.0] - 2020-02-04
### Fixed
- retrieveFile mock was not working with Python < 3.8 in case retrieved file content was bytes.

### Added
- pyndows.get_folder_content listing the content of a folder (non-recursively).
- File type (isDirectory boolean) within mocked SharedFile object.

## [3.2.0] - 2020-01-22
### Fixed
- Allow to store bytes content using Mock.
- Mock is now able to retrieve a file that was previously stored.

### Added
- Mock stored files can now be retrieved with the help of a timeout via `try_get` method.

## [3.1.0] - 2019-12-03
### Added
- Initial release.

[Unreleased]: https://github.com/Colin-b/pyndows/compare/v3.4.0...HEAD
[3.4.0]: https://github.com/Colin-b/pyndows/compare/v3.3.1...v3.4.0
[3.3.1]: https://github.com/Colin-b/pyndows/compare/v3.3.0...v3.3.1
[3.3.0]: https://github.com/Colin-b/pyndows/compare/v3.2.0...v3.3.0
[3.2.0]: https://github.com/Colin-b/pyndows/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/Colin-b/pyndows/releases/tag/v3.1.0
