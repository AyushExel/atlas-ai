# lance_utils/tasks/base.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path
import abc
import pyarrow as pa
from abc import ABC, abstractmethod

class Task(ABC):
    """
    Abstract base class for a task.
    A task defines the schema for the data and provides a way to iterate over the data.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the task."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the task."""
        pass

    @abstractmethod
    def get_schema(self) -> pa.Schema:
        """The schema for the task."""
        pass

    @abstractmethod
    def yield_data(self) -> Generator[Dict[str, Any], None, None]:
        """Yields data for the task."""
        pass

class Annotation(BaseModel):
    """Base model for a single annotation."""
    @classmethod
    @abc.abstractmethod
    def arrow_field(cls) -> pa.Field:
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class Extractor(abc.ABC):
    """Extracts a specific type of annotation from a data source."""
    @abc.abstractmethod
    def extract(self, input_path: Path) -> Dict[str, List[Annotation]]:
        pass

class DataItem:
    """A generic container for a single data point and all its annotations."""
    def __init__(self, item_id: str, image_path: Optional[Path] = None, text_content: Optional[str] = None):
        self.item_id = item_id
        self.image_path = image_path
        self.text_content = text_content
        self.annotations: Dict[str, List[Annotation]] = {}

    def add_annotations(self, key: str, annotations: List[Annotation]):
        self.annotations.setdefault(key, []).extend(annotations)

# --- New Annotation Types ---

class PreferenceData(Annotation):
    """For DPO / RLHF."""
    prompt: str
    chosen: str
    rejected: str

    @classmethod
    def arrow_field(cls) -> pa.Field:
        return pa.field("preference", pa.struct([
            pa.field("prompt", pa.string()),
            pa.field("chosen", pa.string()),
            pa.field("rejected", pa.string())
        ]))

    def to_dict(self) -> Dict[str, Any]:
        return {"prompt": self.prompt, "chosen": self.chosen, "rejected": self.rejected}

class RawText(Annotation):
    """For LLM pre-training."""
    text: str

    @classmethod
    def arrow_field(cls) -> pa.Field:
        return pa.field("text", pa.string())

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text}