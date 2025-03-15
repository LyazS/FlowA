import os
import json
import importlib
from pathlib import Path
import traceback
from typing import Dict, Any
from loguru import logger
from app.nodes.basenode import FABaseNode
from app.uisdk import BaseComponent
from app.schemas.VFlowPlugin import VFProvider


FLOWA_NODE_REGISTRY: Dict[str, VFProvider] = {}
FANODE_REGISTRY: Dict[str, FABaseNode] = {}  # 节点类型与执行类的映射


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
            logger.info(f"Register plugins from {config.Provider}...")
            # 注册节点
            for plugin in config.Plugins:
                if plugin.Type == "FANode":
                    module_path = (
                        f"plugins.{plugin_dir.name}.{Path(plugin.Execute).stem}"
                    )
                    module = importlib.import_module(module_path)
                    node_class: FABaseNode = getattr(module, "EXPORT_NODE")
                    FANODE_REGISTRY[f"@{config.Provider}@{plugin.Name}"] = node_class
                    plugin.CreateInfo = node_class.getNodeCreateInfo()
                    logger.info(f"\tRegister NODE [{plugin.Name}].")
            pass
            # 注册UI组件
            for ui_plugin in config.UIPlugins:
                module_path = (
                    f"plugins.{plugin_dir.name}.{Path(ui_plugin.Component).stem}"
                )
                module = importlib.import_module(module_path)
                ui_component = getattr(module, "EXPORT_UI")
                ui_plugin.Component = ui_component()
                logger.info(f"\tRegister UI [{ui_plugin.Name}].")
            pass
            # 修正icon路径
            config.Icon = f"{plugin_dir.name}/{config.Icon}"
            if not (plugin_dir / config.Icon).exists():
                logger.warning(f"Icon {config.Icon} not found.")

            FLOWA_NODE_REGISTRY[config.Provider] = config
            logger.info(f"\tRegister provider {config.Provider} Done.")
            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            print(f"Error loading plugin {plugin_dir.name}: {errmsg}")
            raise e
