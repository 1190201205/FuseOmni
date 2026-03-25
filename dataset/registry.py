from typing import Type, Dict, Any

from dataset.base.dataset import BaseDataset

DATASET_REGISTRY: Dict[str, Type[BaseDataset]] = {}


def register_dataset(name: str):
    """
    类装饰器：将数据集类注册到全局的大字典 DATASET_REGISTRY 中
    """
    def decorator(cls: Type[BaseDataset]):
        if name in DATASET_REGISTRY:
            # 可以在这里打印警告或者抛异常，目前选择覆盖
            pass
        DATASET_REGISTRY[name] = cls
        return cls
    return decorator


def build_dataset(name: str, **kwargs: Any) -> BaseDataset:
    """
    根据配置中的数据集名称和对应参数，实例化出具体的 Dataset 对象
    """
    if name not in DATASET_REGISTRY:
        raise ValueError(f"Unknown dataset '{name}'. Please make sure it is registered.")
    
    cls = DATASET_REGISTRY[name]
    return cls(**kwargs)
