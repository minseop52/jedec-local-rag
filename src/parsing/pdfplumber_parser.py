from __future__ import annotations

import argparse
import json
from pathlib import Path

import pdfplumber

from page_classifier import analyze_page


def clean_cell(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def table_to_markdown(table: list[list[object]]) -> str:
    if not table:
        return ""

    rows = [[clean_cell(cell) for cell in row] for row in table]

    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return ""

    max_cols = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (max_cols - len(row)) for row in rows]

    header = normalized_rows[0]
    body = normalized_rows[1:]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")

    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def save_page_image(page: pdfplumber.page.Page, image_path: Path, resolution: int = 150) -> bool:
    """
    Save a rendered page image.

    This is important for future multimodal RAG.
    Even if text/table parsing succeeds, the original visual layout may still matter.
    """

    image_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        page_image = page.to_image(resolution=resolution)
        page_image.save(str(image_path), format="PNG")
        return True
    except Exception as exc:
        print(f"Warning: failed to save page image {image_path}: {exc}")
        return False


def parse_pdf(
    pdf_path: Path,
    output_dir: Path,
    max_pages: int | None = None,
    image_resolution: int = 150,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    page_image_dir = output_dir / "page_images"
    page_image_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "pdf_path": str(pdf_path),
        "output_dir": str(output_dir),
        "page_image_dir": str(page_image_dir),
        "pages": [],
    }

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        pages_to_parse = total_pages if max_pages is None else min(max_pages, total_pages)

        for page_index in range(pages_to_parse):
            page = pdf.pages[page_index]
            page_number = page_index + 1

            text = page.extract_text() or ""
            tables = page.extract_tables() or []

            table_row_counts = [len(table) for table in tables]

            analysis = analyze_page(
                text=text,
                table_count=len(tables),
                table_row_counts=table_row_counts,
            )

            page_image_path = page_image_dir / f"page_{page_number:03d}.png"
            image_saved = save_page_image(
                page=page,
                image_path=page_image_path,
                resolution=image_resolution,
            )

            page_markdown_lines = [
                f"# Page {page_number}",
                "",
                "## Page Analysis",
                "",
                f"- Primary type: `{analysis.primary_type}`",
                f"- Content tags: {', '.join(analysis.content_tags) if analysis.content_tags else 'none'}",
                f"- Confidence: {analysis.confidence}",
                f"- Use text index: {analysis.routing['use_text_index']}",
                f"- Use table index: {analysis.routing['use_table_index']}",
                f"- Requires visual context: {analysis.routing['requires_visual_context']}",
                f"- Use vision fallback: {analysis.routing['use_vision_fallback']}",
                f"- Page image saved: {image_saved}",
                f"- Page image path: `{page_image_path}`" if image_saved else "- Page image path: none",
                "",
                "### Reasons",
                "",
            ]

            for reason in analysis.reasons:
                page_markdown_lines.append(f"- {reason}")

            page_markdown_lines.extend(
                [
                    "",
                    "## Extracted Text",
                    "",
                    text.strip(),
                    "",
                    "## Extracted Tables",
                    "",
                ]
            )

            table_infos = []

            for table_index, table in enumerate(tables, start=1):
                markdown_table = table_to_markdown(table)

                page_markdown_lines.extend(
                    [
                        f"### Table {table_index}",
                        "",
                        markdown_table,
                        "",
                    ]
                )

                table_infos.append(
                    {
                        "table_index": table_index,
                        "rows": len(table),
                        "columns": max((len(row) for row in table), default=0),
                        "markdown_preview": markdown_table[:500],
                    }
                )

            page_output_path = output_dir / f"page_{page_number:03d}.md"
            page_output_path.write_text(
                "\n".join(page_markdown_lines),
                encoding="utf-8",
            )

            page_metadata = {
                "page_number": page_number,
                "text_length": len(text),
                "table_count": len(tables),
                "output_file": str(page_output_path),
                "page_image_path": str(page_image_path) if image_saved else None,
                "image_saved": image_saved,
                "analysis": analysis.to_dict(),
                "tables": table_infos,
            }

            # Convenience fields for later pipeline stages.
            page_metadata["primary_type"] = analysis.primary_type
            page_metadata["content_tags"] = analysis.content_tags
            page_metadata["routing"] = analysis.routing

            metadata["pages"].append(page_metadata)

            print(
                f"Parsed page {page_number}/{pages_to_parse} "
                f"- text chars: {len(text)}, tables: {len(tables)}, "
                f"primary_type: {analysis.primary_type}, "
                f"tags: {analysis.content_tags}, "
                f"vision: {analysis.routing['use_vision_fallback']}"
            )

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nDone. Output saved to: {output_dir}")
    print(f"Metadata saved to: {metadata_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse PDF text, tables, metadata, and page images with pdfplumber."
    )
    parser.add_argument("pdf_path", type=Path, help="Path to input PDF file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/parsed"),
        help="Directory to save parsed markdown files",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of pages to parse",
    )
    parser.add_argument(
        "--image-resolution",
        type=int,
        default=150,
        help="Resolution for rendered page images",
    )

    args = parser.parse_args()

    if not args.pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {args.pdf_path}")

    pdf_name = args.pdf_path.stem
    output_dir = args.output_dir / pdf_name

    parse_pdf(
        pdf_path=args.pdf_path,
        output_dir=output_dir,
        max_pages=args.max_pages,
        image_resolution=args.image_resolution,
    )


if __name__ == "__main__":
    main()