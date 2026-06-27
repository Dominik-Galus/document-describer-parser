# document-describer-parser

Convert PDFs to Markdown with automatic figure descriptions using vision-language models.

## Install

```bash
pip install -e .
```

## Usage

```bash
parse-doc input.pdf output_dir --describer paligemma --save-pictures
```

Omit `--describer` to skip figure descriptions. Only `paligemma` is supported currently.

Requires a Hugging Face token in a `.env` file (`HF_TOKEN=...`).
