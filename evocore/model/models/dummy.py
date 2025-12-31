from evocore.model.model_manager import BaseModel


class DummyModel(BaseModel):
    """
    Dummy / reference model.

    This model exists to:
    - verify plugin discovery
    - serve as documentation
    - support testing

    It is NOT intended for production inference.
    """

    name = "dummy"

    def invoke(self, *args, **kwargs):
        return "ok"
