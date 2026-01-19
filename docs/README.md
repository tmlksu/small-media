# Small Media Documentation

This directory contains all project documentation for Small Media - a self-hosted private media player.

## Documentation Structure

| Directory/File | Description |
|----------------|-------------|
| [INSTALLATION.md](./INSTALLATION.md) | Setup and installation instructions |
| [SPECIFICATION.md](./SPECIFICATION.md) | Detailed project specifications |
| [adr/](./adr/) | Architecture Decision Records |
| [specs/](./specs/) | Feature specifications |
| [api/](./api/) | API documentation (OpenAPI) |
| [issues/](./issues/) | Known issues and TODOs |

## Quick Links

- **Getting Started**: See [INSTALLATION.md](./INSTALLATION.md)
- **API Reference**: See [api/openapi.yaml](./api/openapi.yaml)
- **Why decisions were made**: See [adr/](./adr/)

## Living Documents

This documentation follows the "Living Document" approach:

1. **Keep documents up-to-date** when making related code changes
2. **ADRs are immutable** once accepted (create new ADRs to supersede)
3. **Specs evolve** with the project requirements

## Contributing to Documentation

When adding new documentation:

1. Place architectural decisions in `adr/` with format `NNN-title.md`
2. Place feature specs in `specs/`
3. Update this README if adding new top-level documents
