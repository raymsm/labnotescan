# Android implementation plan

## Goals
- Keep conversion logic in Python `core/` and expose only a thin Android wrapper.
- Support user-selected import/export locations via Storage Access Framework (SAF).
- Run OCR/conversion jobs with WorkManager so large PDFs survive app backgrounding.
- Preserve the local-only guarantee: no uploads, no analytics payloads from OCR path.

## Storage Access Framework for import/export
1. **Import input**
   - Use `ActivityResultContracts.OpenDocument` for single files (`image/*`, `application/pdf`, `application/zip`).
   - Use `ActivityResultContracts.OpenDocumentTree` when the user selects a folder of scans.
   - Persist URI permissions with `takePersistableUriPermission`.
2. **Export output**
   - Let users choose a target folder with `OpenDocumentTree`.
   - Write generated markdown and attachments through `DocumentFile` APIs.
3. **URI bridge to core**
   - Resolve SAF URIs into app-cache files before calling `convert(input_uri, output_dir, options)`.
   - After conversion, copy resulting markdown/attachments into the selected export tree.

## Background worker for OCR jobs
1. Queue conversion via `WorkManager` with `OneTimeWorkRequest`.
2. Pass `inputUri`, `outputTreeUri`, and OCR options in worker input data.
3. Run conversion in a foreground service style worker notification for long-running jobs.
4. Publish progress (`setProgress`) for page-level OCR updates.
5. On completion, emit success/failure result and deep-link back to job history screen.

## Local-only processing constraints
- No network permissions required for OCR flow (`INTERNET` omitted in manifest for release flavor).
- Tesseract language files and model assets bundled with app or side-loaded by user.
- Temporary files written only to app-scoped cache and deleted after export.
- Crash/error logs must redact recognized OCR text by default.

## Minimal skeleton status
A starter Android skeleton is included under `android/` with:
- file/folder selection in `MainActivity`
- WorkManager job scheduling
- placeholder `ConversionWorker` showing where the core API bridge is called
