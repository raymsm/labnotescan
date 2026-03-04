# LabNoteScan Android skeleton (minimal)

This directory contains a minimal app skeleton that demonstrates:
- picking files/folders via SAF
- queuing conversion in WorkManager
- exporting markdown to a user-selected directory

The worker currently contains a bridge placeholder where the embedded Python/native layer should invoke shared core conversion API: `convert(input_uri, output_dir, options)`.
