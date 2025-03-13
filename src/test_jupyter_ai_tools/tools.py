import json


def delete_cell(file_path: str, cell_index: int) -> str:
    """
    Remove a cell at a given integer cell index.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        if 0 <= cell_index < len(notebook["cells"]):
            cut_cell = notebook["cells"].pop(cell_index)

            json_str = json.dumps(notebook, indent=2)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            return f"✅ Cut cell {cell_index}: {cut_cell['source']}"
        else:
            return f"❌ Invalid cell ID: {cell_index}"

    except Exception as e:
        return f"❌ Error cutting cell: {str(e)}"


def add_cell(file_path: str, cell_index: int, cell_type: str = "code") -> str:
    """
    Add an empty cell at a given integer cell index. The cell is a code cell by default,
    but can be set to markdown with the string "markdown".
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        new_cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": [],
            "outputs": [] if cell_type == "code" else None
        }

        id = max(0, min(cell_index, len(notebook["cells"])))
        notebook["cells"].insert(id, new_cell)

        json_str = json.dumps(notebook, indent=2)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        return f"✅ Added {cell_type} cell at position {id}."

    except Exception as e:
        return f"❌ Error adding cell: {str(e)}"


def write_to_cell(file_path: str, cell_index: int, content: str) -> str:
    """
    Overwrite the content of an existing cell at a given cell index.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        if 0 <= cell_index < len(notebook["cells"]):
            notebook["cells"][cell_index]["source"] = content.split("\n")

            json_str = json.dumps(notebook, indent=2)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            return f"✅ Updated cell {cell_index} with content:\n{content}"
        else:
            return f"❌ Invalid cell ID: {cell_index}"

    except Exception as e:
        return f"❌ Error writing to cell: {str(e)}"


def read_cell(file_path: str, cell_index: int) -> str:
    """
    Read the full content of a cell at a given integer cell index.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        if 0 <= cell_index < len(notebook["cells"]):
            cell_data = notebook["cells"][cell_index]
            return json.dumps(cell_data, indent=2)
        else:
            return f"❌ Invalid cell ID: {cell_index}"

    except Exception as e:
        return f"❌ Error reading cell: {str(e)}"


def cell_count(file_path: str) -> str:
    """
    Return the total number of cells.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        max_index = len(notebook["cells"]) - 1
        return f"✅ The last cell index is {max_index}."

    except Exception as e:
        return f"❌ Error getting max cell index: {str(e)}"


def read_notebook(file_path: str) -> str:
    """
    Retrieve all cells from a notebook.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        cells_content = [
            f"Cell {i} ({cell['cell_type']}):\n{''.join(cell['source'])}"
            for i, cell in enumerate(notebook["cells"])
        ]

        return "\n\n".join(cells_content)

    except Exception as e:
        return f"❌ Error reading notebook: {str(e)}"
