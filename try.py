import evocore.model.model_manager as model_manager
import time

manager = model_manager.ModelManager()
model_name_list = manager.list_models()
print(model_name_list)

for name in model_name_list:
    if name == "qwen_local":
        continue
    start = time.time()
    model = manager.get_model(name)
    resp = model.invoke("who are you?")
    end = time.time()
    print(name)
    print(resp)
    print(f"time using: {end-start}")
