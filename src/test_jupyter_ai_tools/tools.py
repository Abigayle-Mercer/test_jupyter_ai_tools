import json
import os
import tempfile


def _safe_write_notebook(file_path: str, notebook: dict) -> None:
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp_file:
            json.dump(notebook, tmp_file, indent=2)
            tmp_file_path = tmp_file.name
        os.replace(tmp_file_path, file_path)
    except Exception as e:
        raise RuntimeError(f"❌ Failed atomic write: {e}")


def _safe_load_notebook(file_path: str) -> dict:
    try:
        if os.path.getsize(file_path) == 0:
            raise ValueError("Notebook file is empty!")

        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        if "cells" not in notebook or not isinstance(notebook["cells"], list):
            raise ValueError("Notebook is malformed or missing 'cells' list")

        return notebook
    except Exception as e:
        raise RuntimeError(f"❌ Error loading notebook: {e}")


def delete_cell(file_path: str, cell_index: int) -> str:
    try:
        notebook = _safe_load_notebook(file_path)

        if 0 <= cell_index < len(notebook["cells"]):
            cut_cell = notebook["cells"].pop(cell_index)
            _safe_write_notebook(file_path, notebook)
            return f"✅ Cut cell {cell_index}: {cut_cell['source']}"
        else:
            return f"❌ Invalid cell ID: {cell_index}"
    except Exception as e:
        return str(e)


def add_cell(file_path: str, cell_index: int, cell_type: str = "code") -> str:
    try:
        notebook = _safe_load_notebook(file_path)

        new_cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": [],
            "outputs": [] if cell_type == "code" else None
        }

        id = max(0, min(cell_index, len(notebook["cells"])))
        notebook["cells"].insert(id, new_cell)
        _safe_write_notebook(file_path, notebook)
        return f"✅ Added {cell_type} cell at position {id}."
    except Exception as e:
        return f"❌ Error adding cell: {str(e)}"


def write_to_cell(file_path: str, cell_index: int, content: str) -> str:
    try:
        notebook = _safe_load_notebook(file_path)

        if 0 <= cell_index < len(notebook["cells"]):
            notebook["cells"][cell_index]["source"] = content.split("\n")
            _safe_write_notebook(file_path, notebook)
            return f"✅ Updated cell {cell_index} with content:\n{content}"
        else:
            return f"❌ Invalid cell ID: {cell_index}"
    except Exception as e:
        return f"❌ Error writing to cell: {str(e)}"


def read_cell(file_path: str, cell_index: int) -> str:
    try:
        notebook = _safe_load_notebook(file_path)

        if 0 <= cell_index < len(notebook["cells"]):
            cell_data = notebook["cells"][cell_index]
            return json.dumps(cell_data, indent=2)
        else:
            return f"❌ Invalid cell ID: {cell_index}"
    except Exception as e:
        return f"❌ Error reading cell: {str(e)}"


def cell_count(file_path: str) -> str:
    try:
        notebook = _safe_load_notebook(file_path)
        max_index = len(notebook["cells"]) - 1
        return f"✅ The last cell index is {max_index}."
    except Exception as e:
        return f"❌ Error getting max cell index: {str(e)}"


def read_notebook(file_path: str) -> str:
    try:
        notebook = _safe_load_notebook(file_path)
        cells_content = [
            f"Cell {i} ({cell['cell_type']}):\n{''.join(cell['source'])}"
            for i, cell in enumerate(notebook["cells"])
        ]
        return "\n\n".join(cells_content)
    except Exception as e:
        return f"❌ Error reading notebook: {str(e)}"
