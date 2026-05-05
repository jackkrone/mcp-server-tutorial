# official python mcp server sdk
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base


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

@mcp.prompt(
    name="format",
    description="Rewrites the content of the document in markdown format"
)
def format_document(
    doc_id: str = Field(description="The id of the document to format")
) -> list[base.Message]:
    prompt = f"""
        Your goal is to reformat a document with markdown syntax.

        The id of the document you need to reformat is:
        <document_id>
        {doc_id}
        </document_id>

        Please read the contents of the document above. Your task is to rewrite the entire document using markdown formatting, applying the following rules:

        - Ensure all existing section titles or headings in the original document are formatted as appropriate Markdown headers (e.g., "#", "##", "###", etc.).
        - Identify major topics or sections; use higher-level headers (e.g., "#") for document title or main headings, and lower levels ("##", "###") for subsections as needed.
        - Use bullet points or numbered lists where appropriate.
        - Convert any tables or lists in the original document to valid markdown syntax.
        - Format code blocks with triple backticks and syntax highlighting if possible.
        - Emphasize important terms with bold (**term**) or italics (*term*).
        - Do not omit any content; retain all the information.
        - The output should be only the reformatted document, with no explanation or comments.

        Return only the rewritten document in markdown format.
   
        """

    return [base.UserMessage(prompt)]


# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
