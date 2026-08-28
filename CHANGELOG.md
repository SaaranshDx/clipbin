# Changelog

All notable changes are listed below in chronological order.

## 2026-08-24

- `be91b4e` — Initial commit.
- `e20cd3e` — Added the paste creation endpoint.
- `e970e9e` — Added paste reading.
- `3257107` — Added paste creation metadata and persistence duration.
- `2c3958e` — Improved metadata-writing error handling.

## 2026-08-25

- `65a02ec` — Added duration-based paste cleanup and improved error handling.
- `2e0b293` — Added the HTTP server for paste creation and viewing.
- `b4f2e13` — Migrated the server to FastAPI with paste endpoints.
- `e20c373` — Added custom HTTP exception handling.
- `e160a12` — Added a seven-day fallback duration.
- `53a4f5b` — Replaced UUIDs with random paste IDs.
- `dd9f634` — Removed several function docstrings for clarity.
- `a26ea24` — Changed paste retrieval to return raw text.
- `7ecced7` — Added CORS middleware.

## 2026-08-26

- `46e55f3` — Added frontend paste creation.
- `5a432f0` — Implemented the paste creation UI and metadata files.
- `2b94bb9` — Added the raw paste HTML endpoint.
- `d0fdab7` — Corrected the raw paste HTML MIME type.
- `ceff319` — Added the frontend stylesheet.
- `255af3e` — Added the CSS-serving endpoint.
- `3349f16` — Rebranded the project.
- `437878f` — Corrected created-paste URL formatting.
- `ca337d4` — Added GitHub and CLI buttons with styling.
- `7d76206` — Added the API reference modal and styles.
- `9e09295` — Added the root endpoint and corrected resource linking.
- `f4ae194` — Made the frontend API URL dynamic.
- `31dc38a` — Corrected the project root path.
- `aab05ff` — Updated dependencies.
- `3e324bb` — Corrected upload URL formatting.

## 2026-08-27

- `624ba1d` — Set a static API URL for frontend consistency.
- `a024850` — Added a trailing slash to the API URL.
- `ae7f022` — Corrected the API endpoint URL.
- `d3ff537` — Added browser encryption helpers.
- `53f7e07` — Added optional encryption before upload.
- `42cf11d` — Added paste decryption with a user key.
- `0753a3f` — Added optional-encryption controls and key modals.
- `5536bad` — Exposed paste encryption status.
- `8d10eca` — Ignored the database directory.
- `1d4baf7` — Added a GitHub Actions repository-mirroring workflow.
- `a061781` — Updated the mirror token.
- `103f6f7` — Removed the repository-mirroring workflow.
- `ae8055e` — Updated the API base URL documentation.
- `c678874` — Documented optional paste encryption.
- `b3ced3c` — Updated the API base URL to Clipbin.
- `b47a14f` — Updated dependencies.
- `7279ed0` — Added the initial CLI entry point.
- `a5fc31b` — Added CLI argument parsing.

## 2026-08-28

- `b038187` — Added CLI paste uploads from stdin with custom duration.
- `fdf2ce5` — Added CLI AES-GCM encryption.
- `177b045` — Improved CLI input, encryption, API, and cancellation error handling.
- `60d6525` — Added CLI paste retrieval by ID or URL with redirect support.
- `9746d75` — Added CLI encrypted-paste decryption.
- `e09e540` — Added Linux and macOS PyInstaller workflows.
- `fd382ac` — Added CLI upload, encryption, decryption, retrieval, and failure tests.
- `74ef573` — Added the local PowerShell compiler script.
- `f0fcb4f` — Ignored CLI build artifacts.
- `cc6287c` — Added the standalone `/api` documentation page.
- `1d40876` — Added detailed CLI usage and encryption documentation.
