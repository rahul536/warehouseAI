import argparse
import base64
import hashlib
import json
import mimetypes
import os
from pathlib import Path

import chromadb
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DIR = PROJECT_ROOT / "knowledge_base" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "knowledge_base" / "processed"
VECTOR_DIR = PROJECT_ROOT / "knowledge_base" / "vector_store"

COLLECTION_NAME = "warehouse_knowledge"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
EMBED_BATCH_SIZE = 50

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

VISION_MODEL = os.getenv(
    "RAG_VISION_MODEL",
    "gpt-5.4-mini",
)


def file_hash(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def relative_path(file_path: Path) -> str:
    return str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def create_id(*values: str) -> str:
    joined = "|".join(values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def split_text(text: str) -> list[str]:
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def make_record(
    text: str,
    source_path: Path,
    source_type: str,
    locator: str,
    chunk_number: int,
    extra_metadata: dict | None = None,
) -> dict:
    metadata = {
        "source_file": relative_path(source_path),
        "asset_path": relative_path(source_path),
        "source_type": source_type,
        "locator": locator,
        "file_hash": file_hash(source_path),
        "chunk_number": chunk_number,
    }

    if extra_metadata:
        metadata.update(extra_metadata)

    return {
        "id": create_id(
            metadata["source_file"],
            source_type,
            locator,
            str(chunk_number),
            text,
        ),
        "text": text,
        "metadata": metadata,
    }


def extract_text_file(file_path: Path) -> list[dict]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    chunks = split_text(content)

    return [
        make_record(
            text=chunk,
            source_path=file_path,
            source_type="text",
            locator="full_document",
            chunk_number=index,
        )
        for index, chunk in enumerate(chunks)
    ]


def extract_pdf(file_path: Path, report: dict) -> list[dict]:
    records = []
    reader = PdfReader(str(file_path))
    pages_with_text = 0

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        chunks = split_text(page_text)

        if chunks:
            pages_with_text += 1

        for chunk_number, chunk in enumerate(chunks):
            records.append(
                make_record(
                    text=chunk,
                    source_path=file_path,
                    source_type="pdf_text",
                    locator=f"page_{page_number}",
                    chunk_number=chunk_number,
                    extra_metadata={"page": page_number},
                )
            )

    if pages_with_text == 0:
        report["needs_ocr"].append(relative_path(file_path))

    return records


def table_rows_to_text(
    table_name: str,
    headers: list[str],
    rows: list[list[str]],
) -> str:
    lines = [
        f"Table: {table_name}",
        f"Columns: {', '.join(headers)}",
        "Rows:",
    ]

    for row in rows:
        values = [
            f"{header}: {value}"
            for header, value in zip(headers, row)
        ]
        lines.append(" | ".join(values))

    return "\n".join(lines)


def extract_csv(file_path: Path) -> list[dict]:
    dataframe = pd.read_csv(file_path).fillna("").astype(str)

    return dataframe_to_records(
        dataframe=dataframe,
        source_path=file_path,
        table_name=file_path.stem,
    )


def extract_excel(file_path: Path) -> list[dict]:
    records = []
    workbook = pd.ExcelFile(file_path)

    for sheet_name in workbook.sheet_names:
        dataframe = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
        ).fillna("").astype(str)

        records.extend(
            dataframe_to_records(
                dataframe=dataframe,
                source_path=file_path,
                table_name=sheet_name,
            )
        )

    return records


def dataframe_to_records(
    dataframe: pd.DataFrame,
    source_path: Path,
    table_name: str,
) -> list[dict]:
    records = []
    headers = list(dataframe.columns)
    row_group_size = 20

    for start in range(0, len(dataframe), row_group_size):
        end = min(start + row_group_size, len(dataframe))
        rows = dataframe.iloc[start:end].values.tolist()

        text = table_rows_to_text(
            table_name=table_name,
            headers=headers,
            rows=rows,
        )

        records.append(
            make_record(
                text=text,
                source_path=source_path,
                source_type="table",
                locator=f"{table_name}_rows_{start + 1}_to_{end}",
                chunk_number=start // row_group_size,
                extra_metadata={
                    "table_name": table_name,
                    "row_start": start + 1,
                    "row_end": end,
                },
            )
        )

    return records


def describe_image(file_path: Path) -> str:
    mime_type = mimetypes.guess_type(file_path.name)[0] or "image/png"
    encoded_image = base64.b64encode(file_path.read_bytes()).decode("utf-8")

    client = OpenAI()

    response = client.responses.create(
        model=VISION_MODEL,
        store=False,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Describe this warehouse image for retrieval. "
                            "Include visible labels, equipment, locations, "
                            "process steps, warnings, and relevant quantities. "
                            "Do not invent details."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:{mime_type};base64,{encoded_image}"
                        ),
                    },
                ],
            }
        ],
    )

    return response.output_text.strip()


def extract_image(
    file_path: Path,
    caption_images: bool,
    report: dict,
) -> list[dict]:
    asset = {
        "source_file": relative_path(file_path),
        "asset_path": relative_path(file_path),
        "source_type": "image",
        "file_hash": file_hash(file_path),
    }

    report["image_assets"].append(asset)

    if not caption_images:
        report["images_pending_caption"].append(relative_path(file_path))
        return []

    caption = describe_image(file_path)

    return [
        make_record(
            text=f"Image description: {caption}",
            source_path=file_path,
            source_type="image",
            locator="image_asset",
            chunk_number=0,
        )
    ]


def embed_records(records: list[dict]) -> list[list[float]]:
    client = OpenAI()
    embeddings = []

    for start in range(0, len(records), EMBED_BATCH_SIZE):
        batch = records[start:start + EMBED_BATCH_SIZE]
        texts = [record["text"] for record in batch]

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )

        ordered = sorted(response.data, key=lambda item: item.index)
        embeddings.extend([item.embedding for item in ordered])

    return embeddings


def index_records(records: list[dict]) -> None:
    if not records:
        return

    client = chromadb.PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "WarehouseAI SOP and knowledge-base index"},
    )

    embeddings = embed_records(records)

    collection.upsert(
        ids=[record["id"] for record in records],
        documents=[record["text"] for record in records],
        metadatas=[record["metadata"] for record in records],
        embeddings=embeddings,
    )


def ingest(caption_images: bool) -> dict:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "indexed_chunks": 0,
        "needs_ocr": [],
        "images_pending_caption": [],
        "image_assets": [],
        "skipped_files": [],
    }

    records = []

    supported_images = {".png", ".jpg", ".jpeg", ".webp"}

    for file_path in RAW_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        try:
            if extension in {".txt", ".md"}:
                records.extend(extract_text_file(file_path))

            elif extension == ".pdf":
                records.extend(extract_pdf(file_path, report))

            elif extension == ".csv":
                records.extend(extract_csv(file_path))

            elif extension in {".xlsx", ".xls"}:
                records.extend(extract_excel(file_path))

            elif extension in supported_images:
                records.extend(
                    extract_image(
                        file_path,
                        caption_images,
                        report,
                    )
                )

            else:
                report["skipped_files"].append(relative_path(file_path))

        except Exception as error:
            report["skipped_files"].append(
                f"{relative_path(file_path)} — {type(error).__name__}"
            )

    index_records(records)

    report["indexed_chunks"] = len(records)

    (PROCESSED_DIR / "chunks.json").write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    (PROCESSED_DIR / "ingestion_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest WarehouseAI knowledge-base files."
    )
    parser.add_argument(
        "--caption-images",
        action="store_true",
        help="Generate searchable captions for standalone image files.",
    )

    args = parser.parse_args()
    result = ingest(caption_images=args.caption_images)

    print(json.dumps(result, indent=2))