# MCP Tool Schema & Example Requests

This document describes the MCP tools exposed by `mcp_server.py`, including input parameters, default values, output structure, and example requests.

## Overview

Server name: `base-editor-design-tool`

Tools:
- `design_guides`
- `design_guides_multiple`

## Tool: design_guides

Runs base editor guide design for a single set of parameters. Wraps `base_editing_guide_designs.py`.

### Input schema (JSON-style)

```
{
  "type": "object",
  "properties": {
    "input_file": { "type": "string", "description": "Path to transcript list (.txt) or FASTA file." },
    "input_type": { "type": "string", "description": "Type of input: transcript list or nucleotide sequence." },
    "output_name": { "type": "string", "description": "Output folder name prefix." },
    "variant_file": { "type": "string", "default": "variant_summary.txt", "description": "ClinVar variant file." },
    "be_type": { "type": "string", "default": "", "description": "Base editor type; if empty, use PAM/edit window parameters." },
    "pam": { "type": "string", "default": "NGG", "description": "PAM sequence (used when be_type is empty)." },
    "edit_window": { "type": "string", "default": "4-8", "description": "Edit window relative to sgRNA (used when be_type is empty)." },
    "sg_len": { "type": "integer", "default": 20, "description": "sgRNA length excluding PAM (used when be_type is empty)." },
    "edit": { "type": "string", "default": "all", "description": "Edit type: C->T, A->G, or all (used when be_type is empty)." },
    "intron_buffer": { "type": "integer", "default": 30, "description": "Number of bp into intron for guide design." },
    "filter_gc": { "type": "boolean", "default": false, "description": "Filter edits in a GC motif." }
  },
  "required": ["input_file", "input_type", "output_name"]
}
```

### Output schema (JSON-style)

```
{
  "type": "object",
  "properties": {
    "ok": { "type": "boolean" },
    "output_folder": { "type": ["string", "null"], "description": "Latest output folder matching output_name prefix." },
    "new_output_dirs": { "type": "array", "items": { "type": "string" } },
    "stdout": { "type": "string" },
    "stderr": { "type": "string" },
    "returncode": { "type": "integer" }
  },
  "required": ["ok", "output_folder", "new_output_dirs", "stdout", "stderr", "returncode"]
}
```

### Example request (single run, be_type provided)

```
{
  "tool": "design_guides",
  "arguments": {
    "input_file": "Sample_data/example_transcripts.txt",
    "input_type": "transcript",
    "output_name": "AATD_ABE710",
    "variant_file": "variant_summary.txt",
    "be_type": "ABE7.10",
    "intron_buffer": 30,
    "filter_gc": false
  }
}
```

### Example request (single run, custom PAM/edit window)

```
{
  "tool": "design_guides",
  "arguments": {
    "input_file": "Sample_data/example_fasta.fa",
    "input_type": "sequence",
    "output_name": "Custom_BE",
    "pam": "NGG",
    "edit_window": "4-8",
    "sg_len": 20,
    "edit": "all",
    "intron_buffer": 30,
    "filter_gc": true
  }
}
```

## Tool: design_guides_multiple

Runs base editor guide design for multiple BE types or parameter rows. Wraps `multiple_designs.py`.

### Input schema (JSON-style)

```
{
  "type": "object",
  "properties": {
    "input_file": { "type": "string", "description": "Path to transcript list (.txt) or FASTA file." },
    "input_type": { "type": "string", "description": "Type of input: transcript list or nucleotide sequence." },
    "be_file": { "type": "string", "description": "Base editor parameter file." },
    "be_type": { "type": "string", "description": "Base editor type to use from be_file." },
    "output_prefix": { "type": "string", "description": "Prefix for output folders." }
  },
  "required": ["input_file", "input_type", "be_file", "be_type", "output_prefix"]
}
```

### Output schema (JSON-style)

```
{
  "type": "object",
  "properties": {
    "ok": { "type": "boolean" },
    "new_output_dirs": { "type": "array", "items": { "type": "string" } },
    "stdout": { "type": "string" },
    "stderr": { "type": "string" },
    "returncode": { "type": "integer" }
  },
  "required": ["ok", "new_output_dirs", "stdout", "stderr", "returncode"]
}
```

### Example request (batch run)

```
{
  "tool": "design_guides_multiple",
  "arguments": {
    "input_file": "Sample_data/example_transcripts.txt",
    "input_type": "transcript",
    "be_file": "Sample_data/be_types.tsv",
    "be_type": "ABE",
    "output_prefix": "AATD_batch"
  }
}
```

## Notes

- `input_type` must match what the underlying scripts expect (e.g., `transcript` or `sequence`).
- When `be_type` is provided for `design_guides`, the `pam`, `edit_window`, `sg_len`, and `edit` parameters are ignored.
- Outputs are created in the repository root; `output_folder` returns the most recently modified folder matching the given prefix.
