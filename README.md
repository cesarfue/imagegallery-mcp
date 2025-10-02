# ImageGallery MCP Server

This project implements an **MCP (Model Context Protocol) server** that provides image gallery search and retrieval capabilities. It is designed to be used with Claude or any MCP-compatible client. The server can index images, run similarity search using CLIP, and return results to the client.

## Features

- Serve an image gallery to Claude via the MCP protocol  
- Store and manage image embeddings using ChromaDB  
- Perform semantic search with OpenAI CLIP  
- Support for mounting host directories into the container for persistence

## Requirements

- Docker (with Docker Compose if desired)  
- Python 3.11 (inside container)  
- Claude desktop app (or other MCP-compatible client)

## Installation

1. Clone this repository:
   ```
   bash git clone https://github.com/your-username/imagegallery-mcp.git cd
   imagegallery-mcp
   ```

Build the Docker image:

``` docker build -t imagegallery-mcp . 
```

2. Usage

Run the server in a container with bind-mounted volumes to access your local files:

```
docker run -it --rm \ -v $(pwd)/gallery:/app/gallery \ -v
$(pwd)/chroma_db:/app/chroma_db \ -v $(pwd)/results:/app/results \
imagegallery-mcp ```


This makes the following directories available inside the container:

gallery/ – your image collection

chroma_db/ – the ChromaDB database storing embeddings

results/ – search results and metadata

Claude Configuration

To connect this server to Claude, add an entry to your Claude MCP config file (usually located at ~/Library/Application Support/Claude/config.json on macOS):

