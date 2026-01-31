import os
import sys
import subprocess
import tempfile
from typing import Dict, List, Optional

from fastmcp import FastMCP


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
mcp = FastMCP("base-editor-design-tool")


def _bool_to_str(value: bool) -> str:
    return "True" if value else "False"


def _list_output_dirs() -> List[str]:
    return [
        name
        for name in os.listdir(REPO_ROOT)
        if os.path.isdir(os.path.join(REPO_ROOT, name))
    ]


def _find_latest_output(prefix: str) -> Optional[str]:
    candidates = []
    for name in _list_output_dirs():
        if name.startswith(prefix + "_"):
            path = os.path.join(REPO_ROOT, name)
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def _run_cmd(cmd: List[str]) -> Dict[str, str]:
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    return {
        "returncode": str(result.returncode),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _normalize_input_text(input_text: str) -> str:
    content = input_text.strip()
    if not content:
        return ""
    if content.startswith(">"):
        return content + "\n"
    # Wrap raw sequence as FASTA with a default header.
    seq = "".join(content.split())
    lines = [seq[i : i + 60] for i in range(0, len(seq), 60)]
    return ">sequence_1\n" + "\n".join(lines) + "\n"


def _write_temp_input(content: str, suffix: str) -> str:
    tmp_dir = os.path.join(REPO_ROOT, ".mcp_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    fd, path = tempfile.mkstemp(dir=tmp_dir, prefix="mcp_input_", suffix=suffix, text=True)
    with os.fdopen(fd, "w") as handle:
        handle.write(content)
    return path


def _prepare_input_file(input_text: str) -> str:
    normalized = _normalize_input_text(input_text)
    if not normalized:
        raise ValueError("input_text is empty after normalization")
    return _write_temp_input(normalized, ".fa")

@mcp.tool()
def design_guides(
    output_name: str,
    input_text: str = "",
    variant_file: str = "variant_summary.txt",
    be_type: str = "",
    pam: str = "NGG",
    edit_window: str = "4-8",
    sg_len: int = 20,
    edit: str = "all",
    intron_buffer: int = 30,
    filter_gc: bool = False,
) -> Dict[str, object]:
    """
    Run base editor guide design for a single set of parameters.
    Returns output folder and command logs.
    """
    resolved_input_file = _prepare_input_file(input_text)
    cmd = [
        sys.executable,
        "base_editing_guide_designs.py",
        "--input-file",
        resolved_input_file,
        "--input-type",
        "nuc",
        "--variant-file",
        variant_file,
        "--output-name",
        output_name,
        "--intron-buffer",
        str(intron_buffer),
        "--filter-gc",
        _bool_to_str(filter_gc),
    ]
    if be_type:
        cmd += ["--be-type", be_type]
    else:
        cmd += [
            "--pam",
            pam,
            "--edit-window",
            edit_window,
            "--sg-len",
            str(sg_len),
            "--edit",
            edit,
        ]
    before = set(_list_output_dirs())
    logs = _run_cmd(cmd)
    after = set(_list_output_dirs())
    new_dirs = sorted(after - before)
    output_folder = _find_latest_output(output_name)
    return {
        "ok": logs["returncode"] == "0",
        "output_folder": output_folder,
        "new_output_dirs": new_dirs,
        "stdout": logs["stdout"],
        "stderr": logs["stderr"],
        "returncode": int(logs["returncode"]),
    }


@mcp.tool()
def design_guides_multiple(
    be_file: str,
    be_type: str,
    output_prefix: str,
    input_text: str = "",
) -> Dict[str, object]:
    """
    Run base editor guide design for multiple BE types or parameter rows.
    Returns the output folders created and command logs.
    """
    resolved_input_file = _prepare_input_file(input_text)
    cmd = [
        sys.executable,
        "multiple_designs.py",
        "--input-file",
        resolved_input_file,
        "--ip-type",
        "nuc",
        "--be-file",
        be_file,
        "--be-type",
        be_type,
        "--output-prefix",
        output_prefix,
    ]
    before = set(_list_output_dirs())
    logs = _run_cmd(cmd)
    after = set(_list_output_dirs())
    new_dirs = sorted(after - before)
    return {
        "ok": logs["returncode"] == "0",
        "new_output_dirs": new_dirs,
        "stdout": logs["stdout"],
        "stderr": logs["stderr"],
        "returncode": int(logs["returncode"]),
    }


if __name__ == "__main__":
    mcp.run()
