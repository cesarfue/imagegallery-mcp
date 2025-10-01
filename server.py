import os
import time

import chromadb
import torch
from fastmcp import FastMCP
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

BASE_OUT_DIR = "./results"
IMAGES_FOLDER = "./gallery"
CHROMA_DB_FOLDER = "./chroma_db"
MAX_DIM = 1024

server = FastMCP("imagegallery-mcp")

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def load_and_resize(image_path: str):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / float(max(w, h))
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    return img


def get_image_embedding(image_path: str):
    img = load_and_resize(image_path)
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    return embedding.squeeze().cpu().numpy().tolist()


def get_text_embedding(query: str):
    inputs = processor(text=[query], return_tensors="pt", padding=True)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)
    return embedding.squeeze().cpu().numpy().tolist()


client = chromadb.PersistentClient(path=CHROMA_DB_FOLDER)
collection = client.get_or_create_collection("images")

if collection.count() == 0:
    print("Indexing images with embeddings...")
    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(IMAGES_FOLDER, filename)
            emb_vector = get_image_embedding(path)

            collection.add(
                documents=[path],
                metadatas=[{"image_path": path}],
                embeddings=[emb_vector],
                ids=[path],  # use file path as unique id
            )
else:
    print("Loading existing index...")


@server.tool(
    name="clip_search",
    description="Find the image most relevant to a query in the user's personnal image gallery",
)
def clip_search(query: str) -> str:
    query_emb = get_text_embedding(query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5,
    )

    if not results["documents"] or not results["documents"][0]:
        return "No relevant images found."

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(BASE_OUT_DIR, f"query_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    output_texts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        img_path = meta["image_path"]
        output_texts.append(f"Found: {img_path}")

    best_path = results["metadatas"][0][0]["image_path"]
    Image.open(best_path).save(os.path.join(out_dir, os.path.basename(best_path)))

    return (
        "\n".join(output_texts)
        + f"\nBest image copied to {out_dir}/{os.path.basename(best_path)}"
    )


if __name__ == "__main__":
    server.run()
