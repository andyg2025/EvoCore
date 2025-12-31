import pytest

from evocore.model.model_manager import (
    ModelManager,
    MODEL_REGISTRY,
    BaseModel,
)


def test_list_models_contains_dummy():
    models = ModelManager.list_models()

    assert "dummy" in models


def test_get_model_returns_instance():
    model = ModelManager.get_model("dummy")

    assert isinstance(model, BaseModel)
    assert model.invoke() == "ok"


def test_get_model_with_config():
    config = {"a": 1}
    model = ModelManager.get_model("dummy", config=config)

    assert model.config == config


def test_get_model_not_found():
    with pytest.raises(ValueError, match="not found"):
        ModelManager.get_model("not_exist")


def test_models_loaded_only_once():
    ModelManager.list_models()
    first_registry = MODEL_REGISTRY.copy()

    ModelManager.list_models()
    second_registry = MODEL_REGISTRY.copy()

    assert first_registry == second_registry


@pytest.mark.parametrize("model_name", ModelManager.list_models())
def test_all_models_connectivity(model_name):

    try:
        model = ModelManager.get_model(model_name)
        result = model.invoke("who are you?")

        assert result is not None, f"Model {model_name} returned None"

    except Exception as e:
        pytest.fail(f"Model '{model_name}' failed connectivity test with error: {e}")
