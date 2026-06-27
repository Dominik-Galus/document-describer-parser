from dataclasses import dataclass, field
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc.document import NodeItem
from docling_core.types.doc.labels import DocItemLabel


@dataclass
class PdfPipelineConfig:
    images_scale: float = 2.0
    generate_table_images: bool = True
    generate_picture_images: bool = True
    do_formula_enrichment: bool = True


DEFAULT_CONFIG = PdfPipelineConfig()


def _to_options(cfg: PdfPipelineConfig) -> PdfPipelineOptions:
    opts = PdfPipelineOptions()
    opts.images_scale = cfg.images_scale
    opts.generate_table_images = cfg.generate_table_images
    opts.generate_picture_images = cfg.generate_picture_images
    opts.do_formula_enrichment = cfg.do_formula_enrichment
    return opts


def create_converter(config: PdfPipelineConfig | None = None) -> DocumentConverter:
    cfg = config or DEFAULT_CONFIG
    return DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=_to_options(cfg))
    })


def extract_items(doc) -> list[NodeItem]:
    pictures = [element for element, _ in doc.iterate_items()
                if element.label == DocItemLabel.PICTURE]
    return pictures
