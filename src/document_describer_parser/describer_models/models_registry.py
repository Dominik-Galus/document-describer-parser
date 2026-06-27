from typing import Callable, Literal

from transformers import PreTrainedModel, ProcessorMixin

from document_describer_parser.describer_models.pali_gemma_describer import initialize_pali_gemma

DeviceStr = Literal["cuda", "cpu", "mps"]
DescriberFactory = Callable[[DeviceStr], tuple[PreTrainedModel, ProcessorMixin]]

_registry: dict[str, DescriberFactory] = {
    "paligemma": initialize_pali_gemma,
}


def get_describer(name: str) -> DescriberFactory:
    try:
        return _registry[name]
    except KeyError:
        raise ValueError(
            f"No describer '{name}' registered. Available: {list(_registry)}"
        ) from None


def register_describer(name: str, factory: DescriberFactory) -> None:
    _registry[name] = factory

