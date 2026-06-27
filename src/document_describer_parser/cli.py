from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tyro

from document_describer_parser.main import parse_document


@dataclass
class Arguments:
    pdf_path: Path
    output_dir: Path
    describer: str | None = None
    save_pictures: bool = False


def main() -> None:
    args = tyro.cli(Arguments)
    parse_document(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir,
        describer=args.describer,
        save_pictures=args.save_pictures,
        progress_callback=lambda stage, cur, tot: print(
            f"\r{stage}: {cur}/{tot}", end="", flush=True
        ),
    )
    print()
