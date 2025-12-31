import abc
import pkgutil
import importlib
import pathlib
from typing import Dict, Type, Any, List

MODEL_REGISTRY: Dict[str, Type["BaseModel"]] = {}
package = __package__


class BaseModel(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name") and cls.name:
            MODEL_REGISTRY[cls.name] = cls

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}

    @abc.abstractmethod
    def invoke(self, *args, **kwargs) -> Any:
        pass


class ModelManager:
    _is_loaded = False

    @classmethod
    def _load_models(cls) -> None:
        if cls._is_loaded:
            return

        if not package:
            raise RuntimeError("ModelManager must be imported as a package")

        models_path = pathlib.Path(__file__).parent / "models"
        if not models_path.exists():
            raise RuntimeError(f"models path not found: {models_path}")

        if not (models_path / "__init__.py").exists():
            raise RuntimeError("models/ must be a Python package")

        for _, module_name, _ in pkgutil.iter_modules([str(models_path)]):
            try:
                importlib.import_module(f"{package}.models.{module_name}")
            except Exception as e:
                raise ImportError(
                    f"Failed to import model module: {package}.models.{module_name}"
                ) from e

        cls._is_loaded = True

    @classmethod
    def reset(cls):
        cls._is_loaded = False

    @classmethod
    def list_models(cls) -> List[str]:
        cls._load_models()
        return list(MODEL_REGISTRY.keys())

    @classmethod
    def get_model(cls, name: str, config: Dict[str, Any] | None = None) -> BaseModel:
        cls._load_models()
        try:
            return MODEL_REGISTRY[name](config=config)
        except KeyError:
            raise ValueError(f"Model '{name}' not found")
