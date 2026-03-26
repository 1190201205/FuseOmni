# FuseOmni 数据集模块 (Dataset Module)

该目录存放了项目中用于加载和处理各种不同形式数据的规范化数据集流。

## 目录结构

```text
dataset/
├── main.py                             # 数据加载的主入口程序，用于根据配置文件动态加载组合数据集
├── registry.py                         # 数据集注册表模块，维护了别名与类的映射关系
├── base/                               # 二级目录，存放核心框架文件
│   └── dataset.py                      # 核心基类 BaseDataset，所有特定的数据集需继承此类
├── sources/                            # 二级目录，统一存放所有业务数据集实现
│   ├── aishell1/                       # 各个独立数据集的三级目录存放实际 python 脚本
│   └── ...
├── bash_scripts/                       # 存放构建数据集、下载、预处理等外部 Bash 侧脚本
└── load_dataset/                       # (遗留配置与特定未分类辅助脚本放置处)
    └── multi_dataset_config.yaml       # 数据聚合配置文件
```

## 基本用法

通过修改 `load_dataset/multi_dataset_config.yaml` （包含各数据集的启用或关闭、挂载根路径、划分 split 控制以及最大载入条数等参数设置），之后执行顶层 `main.py`。

```bash
# 执行主合并流程，终端默认输出：
python -m dataset.main

# 自定义配置文件路径并将多路数据合并转化成指定 jsonl 格式：
python -m dataset.main --config /path/to/custom_config.yaml --output processed_data.jsonl
```

当前已经接入的规范化数据集包括：

- `aishell1`
- `aishell3`
- `voiceassistant400k`
- `mmsu`
- `librispeech`
- `wenetspeech`
- `fleurs`
- `commonvoice`
- `audiocaps`
- `clotho`
- `openhermes25`
- `tulu3_sft_mixture`

## 怎样新增一个数据集处理类

当需要往项目中兼容新的数据集数据格式（举例：`new_dataset`），请遵循以下规范：

1. **建立规范的文件目录**：
   统一在 `sources/` 下面创建一个三级目录。如新建 `sources/new_dataset/`，并在其中创建文件 `new_dataset_dataset.py`。

2. **继承基类并编写内部逻辑**：
   导入 `BaseDataset` 与 `register_dataset` 注册器装饰器。
   需要重写子类的 `load_data(self)`，按照标准对话格式进行转换，追加到预定义好的 `self.samples` 中，并严格响应数量截断。例如：

   ```python
   from pathlib import Path
   from typing import Any
   from dataset.base.dataset import BaseDataset
   from dataset.registry import register_dataset

   @register_dataset("new_dataset")
   class NewDataset(BaseDataset):
       def __init__(self, dataset_root: str | Path, max_samples: int | None = None, **kwargs: Any) -> None:
           # 注意传递 name 取值对应装饰器中的注册字符串
           super().__init__("new_dataset", dataset_root, **kwargs)
           self.max_samples = max_samples
           self.load_data()

       def load_data(self) -> None:
           # 1. 挂载到 self.dataset_root 下面的对应数据位置，进行按行拉取或解析
           # 2. 将数据转化为框架通用的 Messages 格式体系：
           #    {"role": "user", "content": [{"text": "...", "audio_path": "..."}]}
           # 3. 追加有效的 sample 字典至 self.samples 中：
           #    self.samples.append(row_dict)
           # 4. 判断并打断读取：
           #    if self.max_samples is not None and len(self.samples) >= self.max_samples: break
           pass
   ```

3. **登记注册与挂载环境**：
   非常关键：完成类的编写后，前往位于顶部的 `dataset/main.py` 补充引入。确保解释器经过它，注册器能够感应到：
   ```python
   # 在 main.py 中添加：
   import dataset.sources.new_dataset.new_dataset_dataset
   ```

4. **挂载配置 YAML**：
   最后前往配置文件 `multi_dataset_config.yaml`。基于设定的别名 `new_dataset` 进行节点添加与分配数据集的存放空间 `root` 以及相关参数。当前 `main.py` 会将除 `enabled` 和 `root` 以外的字段作为 `kwargs` 透传给对应数据集构造函数，所以像 `split`、`subset`、`language`、`metadata_name` 这类参数都可以直接由 YAML 驱动。


## 进一步新增 Feature 的规范

- **分离职责 (Separation of Concerns)**：数据加载的核心操作及预处理应该被封装到特定的 `sources/xxx/xxx_dataset.py`。如果是不同数据集跨通用的处理函数和公共常量（比如统一的 ID 生成器或者标准化方法），应当提取到 `base/dataset.py` 或者成为公共静态方法。
- **配置驱动设计 (Config-driven)**：新增功能特性如特定语言过滤条件、动态采样等，必须坚持由 `yaml` 文件配置，通过向 `main.py` 解析后，作为 `kwargs` 透传到各个子 `Dataset` 的 `__init__` 函数内处理。
- **系统及网络脚本剥离**：如果拉取、格式化压缩包转化原始数据需要涉及复杂的系统指令，或利用 `curl`、`docker` 处理等，务必将其沉淀并封装为标准的 `.sh` Bash 脚本，且一律放置于 `bash_scripts/` 维护管理。
