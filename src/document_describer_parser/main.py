import re
from dataclasses import dataclass
from pathlib import Path

from docling_core.types.doc.document import NodeItem
from PIL import Image

from document_describer_parser._converter import (
    PdfPipelineConfig,
    create_converter,
    extract_items,
)
from document_describer_parser.describer import DescriberSession, ProgressCallback
from document_describer_parser.prompts import PICTURE_PROMPT


@dataclass
class ParseResult:
    markdown: str
    pictures: list[NodeItem]
    output_dir: Path | None = None


def _notify(cb: ProgressCallback, stage: str, current: int, total: int) -> None:
    if cb:
        cb(stage, current, total)


def _image_from_item(item: NodeItem) -> Image.Image:
    return item.image.pil_image.convert("RGB")


def parse_document(
    pdf_path: Path,
    *,
    output_dir: Path | None = None,
    describer: str | DescriberSession | None = None,
    save_pictures: bool = False,
    progress_callback: ProgressCallback = None,
    pipeline_config: PdfPipelineConfig | None = None,
) -> ParseResult:
    converter = create_converter(pipeline_config)

    _notify(progress_callback, "converting", 0, 0)
    result = converter.convert(pdf_path)
    doc = result.document
    markdown = doc.export_to_markdown()

    pictures = extract_items(doc)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    own_session = None
    if isinstance(describer, str):
        own_session = DescriberSession(describer)
        own_session._ensure_loaded()
        session = own_session
    elif isinstance(describer, DescriberSession):
        session = describer
    else:
        session = None

    try:
        if session and pictures:
            _notify(progress_callback, "describing_pictures", 0, len(pictures))
            for i, pic in enumerate(pictures):
                pil = _image_from_item(pic)
                description = session.describe(pil, PICTURE_PROMPT)
                replacement = (
                    f"<!-- image -->\n\n**[Figure Description]:** {description}"
                )
                markdown = re.sub(
                    r"<!-- image -->", replacement, markdown, count=1
                )
                if save_pictures and output_dir:
                    pil.save(output_dir / f"picture_{i}.png")
                _notify(progress_callback, "describing_pictures", i + 1, len(pictures))

        if output_dir:
            md_path = output_dir / "parsed_document.md"
            md_path.write_text(markdown, encoding="utf-8")

    finally:
        if own_session:
            own_session.close()

    return ParseResult(
        markdown=markdown,
        pictures=pictures,
        output_dir=output_dir,
    )
