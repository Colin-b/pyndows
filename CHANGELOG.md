# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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

[Unreleased]: https://github.com/Colin-b/pyndows/compare/v3.2.0...HEAD
[3.2.0]: https://github.com/Colin-b/pyndows/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/Colin-b/pyndows/releases/tag/v3.1.0
