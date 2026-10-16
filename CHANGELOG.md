# Changelog

All notable changes to mllogs are documented here.

For releases prior to v0.10.0, see
[GitHub Releases](https://github.com/finnpwalsh/mllogs/releases).

## [0.10.0] - 2026-10-16

### Added
- SQLAlchemy Core database integration.
- Chainable query interface with pandas support.
- Simplified model saving and loading.

### Changed
- Redesigned experiment and run tracking.
- Simplified model persistence.

### Removed
- Legacy SQLite implementation.
- General artifact storage.
- Model registry and aliases.
- Unused serializers.

### Breaking Changes
- Previous APIs and database schemas are incompatible.