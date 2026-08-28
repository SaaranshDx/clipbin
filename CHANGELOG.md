# Changelog

## Highlights

- [FastAPI paste API](https://github.com/SaaranshDx/clipbin/commit/b4f2e13) with creation and retrieval endpoints.
- [Frontend paste creation UI](https://github.com/SaaranshDx/clipbin/commit/46e55f3) with duration controls.
- [Optional browser encryption](https://github.com/SaaranshDx/clipbin/commit/0753a3f) using AES-GCM and PBKDF2-SHA-256.
- [CLI uploads and retrieval](https://github.com/SaaranshDx/clipbin/commit/60d6525), including URL support and redirects.
- [CLI encryption and decryption](https://github.com/SaaranshDx/clipbin/commit/9746d75).
- [Cross-platform PyInstaller builds](https://github.com/SaaranshDx/clipbin/commit/e09e540) for Linux and macOS.
- [Standalone API documentation page](https://github.com/SaaranshDx/clipbin/commit/cc6287c).

## Fixes

- [Improved CLI error handling](https://github.com/SaaranshDx/clipbin/commit/177b045) for input, encryption, networking, and API responses.
- [Corrected API URLs](https://github.com/SaaranshDx/clipbin/commit/ae7f022) across the frontend and documentation.
- [Corrected paste URL and raw response formatting](https://github.com/SaaranshDx/clipbin/commit/a26ea24).
- [Added CORS support](https://github.com/SaaranshDx/clipbin/commit/7ecced7).
- [Improved cleanup and metadata error handling](https://github.com/SaaranshDx/clipbin/commit/65a02ec).

## Improvements

- [Duration metadata and automatic cleanup](https://github.com/SaaranshDx/clipbin/commit/3257107).
- [Random six-character paste IDs](https://github.com/SaaranshDx/clipbin/commit/53a4f5b).
- [GitHub, CLI, and API navigation controls](https://github.com/SaaranshDx/clipbin/commit/ca337d4).
- [CLI test coverage](https://github.com/SaaranshDx/clipbin/commit/fd382ac) for uploads, encryption, decryption, retrieval, and failures.
- [Local PowerShell compiler](https://github.com/SaaranshDx/clipbin/commit/74ef573).
- [Detailed CLI and encryption documentation](https://github.com/SaaranshDx/clipbin/commit/1d40876).

## Commits

Every commit since the initial commit is listed below.

### 2026-08-24

- [be91b4e](https://github.com/SaaranshDx/clipbin/commit/be91b4e) — Initial commit.
- [e20cd3e](https://github.com/SaaranshDx/clipbin/commit/e20cd3e) — Added the paste creation endpoint.
- [e970e9e](https://github.com/SaaranshDx/clipbin/commit/e970e9e) — Added paste reading.
- [3257107](https://github.com/SaaranshDx/clipbin/commit/3257107) — Added paste creation metadata and persistence duration.
- [2c3958e](https://github.com/SaaranshDx/clipbin/commit/2c3958e) — Improved metadata-writing error handling.

### 2026-08-25

- [65a02ec](https://github.com/SaaranshDx/clipbin/commit/65a02ec) — Added duration-based paste cleanup and improved error handling.
- [2e0b293](https://github.com/SaaranshDx/clipbin/commit/2e0b293) — Added the HTTP server for paste creation and viewing.
- [b4f2e13](https://github.com/SaaranshDx/clipbin/commit/b4f2e13) — Migrated the server to FastAPI with paste endpoints.
- [e20c373](https://github.com/SaaranshDx/clipbin/commit/e20c373) — Added custom HTTP exception handling.
- [e160a12](https://github.com/SaaranshDx/clipbin/commit/e160a12) — Added a seven-day fallback duration.
- [53a4f5b](https://github.com/SaaranshDx/clipbin/commit/53a4f5b) — Replaced UUIDs with random paste IDs.
- [dd9f634](https://github.com/SaaranshDx/clipbin/commit/dd9f634) — Removed several function docstrings for clarity.
- [a26ea24](https://github.com/SaaranshDx/clipbin/commit/a26ea24) — Changed paste retrieval to return raw text.
- [7ecced7](https://github.com/SaaranshDx/clipbin/commit/7ecced7) — Added CORS middleware.

### 2026-08-26

- [46e55f3](https://github.com/SaaranshDx/clipbin/commit/46e55f3) — Added frontend paste creation.
- [5a432f0](https://github.com/SaaranshDx/clipbin/commit/5a432f0) — Implemented the paste creation UI and metadata files.
- [2b94bb9](https://github.com/SaaranshDx/clipbin/commit/2b94bb9) — Added the raw paste HTML endpoint.
- [d0fdab7](https://github.com/SaaranshDx/clipbin/commit/d0fdab7) — Corrected the raw paste HTML MIME type.
- [ceff319](https://github.com/SaaranshDx/clipbin/commit/ceff319) — Added the frontend stylesheet.
- [255af3e](https://github.com/SaaranshDx/clipbin/commit/255af3e) — Added the CSS-serving endpoint.
- [3349f16](https://github.com/SaaranshDx/clipbin/commit/3349f16) — Rebranded the project.
- [437878f](https://github.com/SaaranshDx/clipbin/commit/437878f) — Corrected created-paste URL formatting.
- [ca337d4](https://github.com/SaaranshDx/clipbin/commit/ca337d4) — Added GitHub and CLI buttons with styling.
- [7d76206](https://github.com/SaaranshDx/clipbin/commit/7d76206) — Added the API reference modal and styles.
- [9e09295](https://github.com/SaaranshDx/clipbin/commit/9e09295) — Added the root endpoint and corrected resource linking.
- [f4ae194](https://github.com/SaaranshDx/clipbin/commit/f4ae194) — Made the frontend API URL dynamic.
- [31dc38a](https://github.com/SaaranshDx/clipbin/commit/31dc38a) — Corrected the project root path.
- [aab05ff](https://github.com/SaaranshDx/clipbin/commit/aab05ff) — Updated dependencies.
- [3e324bb](https://github.com/SaaranshDx/clipbin/commit/3e324bb) — Corrected upload URL formatting.

### 2026-08-27

- [624ba1d](https://github.com/SaaranshDx/clipbin/commit/624ba1d) — Set a static API URL for frontend consistency.
- [a024850](https://github.com/SaaranshDx/clipbin/commit/a024850) — Added a trailing slash to the API URL.
- [ae7f022](https://github.com/SaaranshDx/clipbin/commit/ae7f022) — Corrected the API endpoint URL.
- [d3ff537](https://github.com/SaaranshDx/clipbin/commit/d3ff537) — Added browser encryption helpers.
- [53f7e07](https://github.com/SaaranshDx/clipbin/commit/53f7e07) — Added optional encryption before upload.
- [42cf11d](https://github.com/SaaranshDx/clipbin/commit/42cf11d) — Added paste decryption with a user key.
- [0753a3f](https://github.com/SaaranshDx/clipbin/commit/0753a3f) — Added optional-encryption controls and key modals.
- [5536bad](https://github.com/SaaranshDx/clipbin/commit/5536bad) — Exposed paste encryption status.
- [8d10eca](https://github.com/SaaranshDx/clipbin/commit/8d10eca) — Ignored the database directory.
- [1d4baf7](https://github.com/SaaranshDx/clipbin/commit/1d4baf7) — Added a repository-mirroring workflow.
- [a061781](https://github.com/SaaranshDx/clipbin/commit/a061781) — Updated the mirror token.
- [103f6f7](https://github.com/SaaranshDx/clipbin/commit/103f6f7) — Removed the repository-mirroring workflow.
- [ae8055e](https://github.com/SaaranshDx/clipbin/commit/ae8055e) — Updated the API base URL documentation.
- [c678874](https://github.com/SaaranshDx/clipbin/commit/c678874) — Documented optional paste encryption.
- [b3ced3c](https://github.com/SaaranshDx/clipbin/commit/b3ced3c) — Updated the API base URL to Clipbin.
- [b47a14f](https://github.com/SaaranshDx/clipbin/commit/b47a14f) — Updated dependencies.
- [7279ed0](https://github.com/SaaranshDx/clipbin/commit/7279ed0) — Added the initial CLI entry point.
- [a5fc31b](https://github.com/SaaranshDx/clipbin/commit/a5fc31b) — Added CLI argument parsing.

### 2026-08-28

- [b038187](https://github.com/SaaranshDx/clipbin/commit/b038187) — Added CLI paste uploads from stdin with custom duration.
- [fdf2ce5](https://github.com/SaaranshDx/clipbin/commit/fdf2ce5) — Added CLI AES-GCM encryption.
- [177b045](https://github.com/SaaranshDx/clipbin/commit/177b045) — Improved CLI input, encryption, API, and cancellation error handling.
- [60d6525](https://github.com/SaaranshDx/clipbin/commit/60d6525) — Added CLI paste retrieval by ID or URL with redirect support.
- [9746d75](https://github.com/SaaranshDx/clipbin/commit/9746d75) — Added CLI encrypted-paste decryption.
- [e09e540](https://github.com/SaaranshDx/clipbin/commit/e09e540) — Added Linux and macOS PyInstaller workflows.
- [fd382ac](https://github.com/SaaranshDx/clipbin/commit/fd382ac) — Added CLI upload, encryption, decryption, retrieval, and failure tests.
- [74ef573](https://github.com/SaaranshDx/clipbin/commit/74ef573) — Added the local PowerShell compiler script.
- [f0fcb4f](https://github.com/SaaranshDx/clipbin/commit/f0fcb4f) — Ignored CLI build artifacts.
- [cc6287c](https://github.com/SaaranshDx/clipbin/commit/cc6287c) — Added the standalone `/api` documentation page.
- [1d40876](https://github.com/SaaranshDx/clipbin/commit/1d40876) — Added detailed CLI usage and encryption documentation.
