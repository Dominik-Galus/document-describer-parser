from typing import Literal
import torch
from transformers import PaliGemmaForConditionalGeneration, PaliGemmaProcessor


def initialize_pali_gemma(
    device: Literal["cuda", "cpu", "mps"],
)-> tuple[PaliGemmaForConditionalGeneration, PaliGemmaProcessor]:
    model_id = "google/paligemma-3b-pt-448"

    processor = PaliGemmaProcessor.from_pretrained(model_id)
    model = PaliGemmaForConditionalGeneration.from_pretrained(
        model_id, 
        torch_dtype=torch.bfloat16 if device != "cpu" else torch.float32
    ).to(device)

    return model, processor
