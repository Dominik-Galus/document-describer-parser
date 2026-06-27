from __future__ import annotations

from collections.abc import Callable
from typing import Any

import torch
from PIL import Image
from transformers import PreTrainedModel, ProcessorMixin

from document_describer_parser.describer_models.models_registry import get_describer


ProgressCallback = Callable[[str, int, int], None] | None


def _resolve_device(preferred: str) -> str:
    if preferred != "auto":
        return preferred
    if torch.cuda.is_available():
        return "cuda"
    if torch.mps.is_available():
        return "mps"
    return "cpu"


class DescriberSession:
    def __init__(
        self,
        name: str,
        device: str = "auto",
        max_new_tokens: int = 1024,
        batch_size: int = 1,
    ) -> None:
        self._name = name
        self._device = _resolve_device(device)
        self._max_new_tokens = max_new_tokens
        self._batch_size = batch_size
        self._model: PreTrainedModel | None = None
        self._processor: ProcessorMixin | None = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        factory = get_describer(self._name)
        self._model, self._processor = factory(self._device)

    def describe(self, image: Image.Image, prompt: str) -> str:
        self._ensure_loaded()
        inputs = self._processor(  # type: ignore[misc]
            text=prompt, images=image, return_tensors="pt"
        ).to(self._device)
        prompt_len = inputs.input_ids.shape[1]
        with torch.no_grad():
            output = self._model.generate(  # type: ignore[union-attr]
                **inputs, max_new_tokens=self._max_new_tokens
            )
        generated_ids = output[0][prompt_len:]
        return self._processor.decode(  # type: ignore[misc]
            generated_ids, skip_special_tokens=True
        ).strip()

    def describe_batch(
        self,
        images: list[Image.Image],
        prompt: str,
        progress_callback: ProgressCallback = None,
    ) -> list[str]:
        self._ensure_loaded()
        results: list[str] = []
        total = len(images)
        bs = self._batch_size

        for batch_start in range(0, total, bs):
            batch = images[batch_start : batch_start + bs]
            inputs = self._processor(  # type: ignore[misc]
                text=[prompt] * len(batch),
                images=batch,
                padding=True,
                return_tensors="pt",
            ).to(self._device)
            prompt_len = inputs.input_ids.shape[1]
            with torch.no_grad():
                outputs = self._model.generate(  # type: ignore[union-attr]
                    **inputs, max_new_tokens=self._max_new_tokens
                )
            for j, output in enumerate(outputs):
                generated_ids = output[prompt_len:]
                text = self._processor.decode(  # type: ignore[misc]
                    generated_ids, skip_special_tokens=True
                ).strip()
                results.append(text)
                if progress_callback:
                    progress_callback(batch_start + j + 1, total)
        return results

    def close(self) -> None:
        if self._model is not None:
            del self._model
            del self._processor
            self._model = None
            self._processor = None
            if self._device == "cuda":
                torch.cuda.empty_cache()

    def __enter__(self) -> DescriberSession:
        self._ensure_loaded()
        return self

    def __exit__(self) -> None:
        self.close()
