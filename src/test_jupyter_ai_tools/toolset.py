from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from .tools import (
    delete_cell,
    add_cell,
    write_to_cell,
    read_cell,
    cell_count,
    read_notebook,
)


class DeleteCellInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")
    cell_index: int = Field(description="The integer index of the cell to delete")

class AddCellInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")
    cell_index: int = Field(description="The integer index of the position to insert the new cell")
    cell_type: str = Field(default="code", description="Type of cell: 'code' or 'markdown'")

class WriteToCellInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")
    cell_index: int = Field(description="The integer index of the cell to overwrite")
    content: str = Field(description="The content to write into the cell")

class ReadCellInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")
    cell_index: int = Field(description="The integer index of the cell to read")

class CellCountInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")

class ReadNotebookInput(BaseModel):
    file_path: str = Field(description="Path to the Jupyter notebook")


structured_tools = [
    StructuredTool.from_function(
        func=delete_cell,
        name="delete_cell",
        description="Remove a cell at a given index from a Jupyter notebook",
        args_schema=DeleteCellInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=add_cell,
        name="add_cell",
        description="Add an empty code or markdown cell to a Jupyter notebook at a given index",
        args_schema=AddCellInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=write_to_cell,
        name="write_to_cell",
        description="Overwrite the content of a cell at a particular index in a Jupyter notebook",
        args_schema=WriteToCellInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=read_cell,
        name="read_cell",
        description="Read the full content of a cell at a given integer cell index. This includes its type, execution count, metadata, source content, and output if the cell is a code cell.",
        args_schema=ReadCellInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=cell_count,
        name="cell_count",
        description="Return the number of cells in the notebook (last cell index)",
        args_schema=CellCountInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=read_notebook,
        name="read_notebook",
        description="Retrieve all cells from a notebook in a string format. This includes all of the cells and their order in the notebook, their content, output, cell type, execution count, and other metadata.",
        args_schema=ReadNotebookInput,
        return_direct=True,
    )
]
