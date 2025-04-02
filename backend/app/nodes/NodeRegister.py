import re
import os
import json
import importlib
from pathlib import Path
import traceback
from typing import Dict, Any
from loguru import logger
from app.nodes.BaseNode import FABaseNode
from app.uisdk import BaseComponent
from app.schemas.VFlowPlugin import VFProvider
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFNodeInterface import VFNodeFlag

FLOWA_NODE_REGISTRY: Dict[str, VFProvider] = {}
FANODE_REGISTRY: Dict[str, FABaseNode] = {}  # 节点类型


def path_to_module_str(path):
    # 处理路径并去除扩展名
    module_path = Path(path).with_suffix("")
    # 转换为Posix格式的字符串，并将斜杠替换为点
    return module_path.as_posix().replace("/", ".")


def register_plugins():
    plugins_dir = Path(__file__).parent.parent.parent / "plugins"

    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        config_path = plugin_dir / "config.json"
        if not config_path.exists():
            continue

        try:
            config = VFProvider.model_validate_json(
                config_path.read_text(encoding="utf-8")
            )
            logger.info(
                "=" * 20 + f" Register plugins from [{config.Provider}] " + "=" * 20
            )
            # 注册节点
            for plugin in config.Plugins:
                if plugin.Type == "FANode":
                    module_path = f"plugins.{plugin_dir.name}.{path_to_module_str(plugin.Execute)}"
                    module = importlib.import_module(module_path)
                    node_class: FABaseNode = getattr(module, "EXPORT_NODE")
                    FANODE_REGISTRY[plugin.Name] = node_class
                    plugin.CreateInfo = node_class.getNodeCreateInfo()
                    plugin.CreateInfo.set_label(plugin.Label)
                    plugin.CreateInfo.set_node_type(plugin.Name)

                    logger.info(f"Register NODE [{plugin.Name}].")
            pass
            # 注册UI组件
            for ui_plugin in config.UIPlugins:
                if ui_plugin.Type == "FANode":
                    module_path = f"plugins.{plugin_dir.name}.{path_to_module_str(ui_plugin.Component)}"
                    module = importlib.import_module(module_path)
                    ui_component = getattr(module, "EXPORT_UI")
                    ui_plugin.Component = ui_component()
                    logger.info(f"Register UI   [{ui_plugin.Name}].")
                    pass
            pass
            # 修正icon路径
            config.Icon = f"{plugin_dir.name}/{config.Icon}"
            if not (plugin_dir / config.Icon).exists():
                logger.warning(f"Icon {config.Icon} not found.")

            FLOWA_NODE_REGISTRY[config.Provider] = config
            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            logger.error(f"Error loading plugin [{plugin_dir.name}]: {errmsg}")
            raise e
    # 最后检查嵌套节点的子节点是否存在
    for provider in FLOWA_NODE_REGISTRY.values():
        for plugin in provider.Plugins:
            if plugin.CreateInfo is not None and (
                plugin.CreateInfo.Flag & VFNodeFlag.IsNested
            ):
                for anode in plugin.CreateInfo.Nesting.ANodes.values():
                    if anode.NType not in FANODE_REGISTRY:
                        logger.error(
                            f"Node [{anode.NType}] of [{plugin.Name}] not found in registry."
                        )
                        raise Exception(
                            f"Node [{anode.NType}] of [{plugin.Name}] not found in registry."
                        )
        pass
    logger.info("=" * 20 + f" Register Done. " + "=" * 20)
