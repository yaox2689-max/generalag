import importlib
import logging
import pathlib

from tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    _tools: dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        cls._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    @classmethod
    def get(cls, name: str) -> BaseTool | None:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[str]:
        return list(cls._tools.keys())

    @classmethod
    def get_all(cls) -> dict[str, BaseTool]:
        return dict(cls._tools)

    @classmethod
    def discover(cls, tools_dir: str | pathlib.Path | None = None) -> None:
        if tools_dir is None:
            tools_dir = pathlib.Path(__file__).parent
        else:
            tools_dir = pathlib.Path(tools_dir)

        for py_file in tools_dir.glob("*_tool.py"):
            module_name = f"tools.{py_file.stem}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseTool)
                        and attr is not BaseTool
                    ):
                        instance = attr()
                        cls.register(instance)
            except Exception as e:
                logger.warning("Failed to load tool from %s: %s", py_file.name, e)
