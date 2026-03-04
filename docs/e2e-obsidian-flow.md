# End-to-end sample flow: Screenshot/PDF to Obsidian vault sync

1. User opens the Android app and taps **Pick input**.
2. App launches SAF picker:
   - screenshot/photo (`.png`, `.jpg`)
   - scanned or typed PDF (`.pdf`)
   - zipped capture bundle (`.zip`)
3. User taps **Pick export folder** and selects an Obsidian vault folder (or staging folder synced to vault).
4. App enqueues a background OCR conversion worker.
5. Worker copies input URI to app cache, calls shared API:
   - `convert(input_uri, output_dir, options)`
6. Core pipeline produces markdown + attachments.
7. Worker writes output into selected SAF export directory.
8. Obsidian mobile/desktop sync (iCloud, Syncthing, Git, etc.) picks up new markdown notes.
9. User opens Obsidian and sees generated notes with embedded attachments.

## Example command parity (CLI)
The same flow can be validated on desktop:

```bash
labnotescan convert ./samples/notebook.pdf --out ./MyVault/LabNotes
```

The Android wrapper is designed to call the same core conversion contract.
