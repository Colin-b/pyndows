# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2019-10-28
### Changed
- Do not use fixed first level dependencies.

### Removed
- pyndows.mock (renamed into pyndows.testing).
- pyndows.health_details (renamed into pyndows.check).

### Added
- pyndows.testing (previously pyndows.mock).
- pyndows.check (previously pyndows.health_details).

## [2.0.0] - 2019-08-08
### Changed
- Mocks are now available via mock submodule.

### Fixed
- Avoid requiring pytest even if not listed in dependencies

## [1.1.0] - 2019-08-06
### Changed
- Switch to pytest.
- Mock is now available via a pytest fixture (see README for details)

### Removed
- mock function is not available anymore. Use the pytest fixture instead

## [1.0.1] - 2019-05-09
### Added
- Initial release.

[Unreleased]: https://github.tools.digital.engie.com/gempy/pyndows/compare/v3.0.0...HEAD
[3.0.0]: https://github.tools.digital.engie.com/gempy/pyndows/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.tools.digital.engie.com/gempy/pyndows/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.tools.digital.engie.com/gempy/pyndows/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.tools.digital.engie.com/gempy/pyndows/releases/tag/v1.0.1
