import uuid
import json
import io
import re
import urllib.request
import urllib.parse
from PIL import Image
import base64
from pydantic import BaseModel, ConfigDict
from contextlib import asynccontextmanager
from loguru import logger
from typing import List, Union, Dict, Any, Optional
from enum import StrEnum
import websockets
import aiohttp


class ComfyUISDK:
    def __init__(self):
        self._url = None
        self._client_id = str(uuid.uuid4())
        self._obj_infos = None

    async def _request_post(self, url, data, decodejson=True):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    response.raise_for_status()
                    if decodejson:
                        return await response.json()
                    else:
                        return await response.read()
            except Exception as ex:
                logger.error(f"Request error: {ex}")
                return None

    async def _request_get(self, url, params=None, jsondec=False):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    if jsondec:
                        return await response.json()
                    else:
                        return await response.read()
            except Exception as ex:
                logger.error(f"Request error: {ex}")
                return None

    async def check(self, url):
        if self._url is not None:
            return True
        _url = re.sub(r"/$", "", url)
        """
        测试url是否能够连通
        """
        logger.debug("Checking ComfyUI object_info")
        self._obj_infos = await self._request_get(f"{_url}/object_info", jsondec=True)
        if self._obj_infos is None:
            logger.error("Failed to get object_info")
            return False
        else:
            logger.success("Got object_info")
            self._url = _url
            return True

    def getBackendConfig(self):
        return self._obj_infos

    async def _queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self._client_id}
        data = json.dumps(p)
        url = f"{self._url}/prompt"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                return json.loads(response_text)

    def find_save_image_node(self, prompt):
        for node_id, node_info in prompt.items():
            if node_info["class_type"] == "SaveImageWebsocket":
                return node_id
        return None

    async def get_images(self, prompt):
        # 找到SaveImageWebsocket的NodeID
        save_image_node_id = self.find_save_image_node(prompt)
        if save_image_node_id is None:
            raise Exception("SaveImageWebsocket not found in prompt")

        # 首先异步队列提示
        prompt_response = await self._queue_prompt(prompt)
        prompt_id = prompt_response["prompt_id"]
        output_images = {}
        current_node = ""

        # 创建WebSocket连接
        modified_api_base = re.sub(r"^https?://|/$", "", self._url)
        async with websockets.connect(
            f"ws://{modified_api_base}/ws?clientId={self._client_id}"
        ) as ws:
            while True:
                out = await ws.recv()
                logger.debug(f"Received: {out}")
                if isinstance(out, str):
                    message = json.loads(out)
                    if message["type"] == "executing":
                        data = message["data"]
                        # if "prompt_id" in data and data["prompt_id"] == prompt_id:
                        if data["node"] is None:
                            break  # 执行完成
                        else:
                            current_node = data["node"]
                else:
                    if current_node == save_image_node_id:
                        images_output: list = output_images.get(current_node, [])
                        image_data = out[8:]
                        images_output.append(Image.open(io.BytesIO(image_data)))
                        output_images[current_node] = images_output

        return output_images.get(current_node, [])
