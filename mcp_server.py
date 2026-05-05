# official python mcp server sdk
from multiprocessing import Value
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name="read_doc_contents",
    # normally make a really clear description so claude knows how to use it
    description="Read the contents of a document and return it as a string",
)
def read_document(
    doc_id: str = Field(description="The id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    
    return docs[doc_id]

@mcp.tool(
    name="edit_document",
    description="Edit the contents of a document and return it as a string",
)
def edit_document(
    doc_id: str = Field(description="The id of the document to edit"),
    old_string: str = Field(description="The text to replace"),
    new_string: str = Field(description="The new text to replace the old text with"),
):
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")

    docs[doc_id] = docs[doc_id].replace(old_string, new_string)

# somehow having this resource defined makes it accessible with the @ character in the terminal... wouldn't there be latency if the mcp_server was on a different machine than the mcp client or if the mcp server had to fetch the resources from some DB?
@mcp.resource(
    "docs://documents",
    # resources can return any type of data, so this is just a hint to the client what the data type is so it can handle it appropriately
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found")
    return docs[doc_id]


# TODO: Write a prompt to rewrite a doc in markdown format
# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
