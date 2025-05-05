import uuid
import json
import io
import re
from PIL import Image
import base64
from pydantic import BaseModel, ConfigDict
from contextlib import asynccontextmanager
from loguru import logger
from typing import List, Union
from enum import StrEnum
import websockets
import aiohttp


class AiDrawResultType(StrEnum):
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"


class AiDrawResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    aitype: AiDrawResultType
    result: List[Image.Image]
    videofps: Union[int, None] = None
    pass


@asynccontextmanager
async def websocket_connect(url):
    try:
        async with websockets.connect(
            url,
            ping_interval=1,
            ping_timeout=1800,
            ssl=None,
        ) as ws:
            logger.debug(f"WebSocket connected to {url}")
            yield ws
            logger.info("WebSocket connection closed")
    except Exception as ex:
        raise Exception("WebSocket connection error: " + str(ex))


def fetchImgsFromNode(node_id, images_by_nodes, ftype=2):
    imgs = []
    if node_id in images_by_nodes:
        for image_data in images_by_nodes[node_id]:
            if ftype == 0:
                image = Image.open(io.BytesIO(image_data))
                imgs.append(image)
            elif ftype == 1:
                base64_image = base64.b64encode(image_data).decode("utf-8")
                imgs.append(base64_image)
            elif ftype == 2:
                imgs.append(image_data)
    return imgs


class ComfyUISDK:
    def __init__(self):
        self.url = None
        self._client_id = str(uuid.uuid4())
        self._obj_infos = None

    def useUrl(self, url: str):
        url = re.sub(r"/$", "", url)
        self.url = url
        logger.info(f"Using ComfyUI URL: {self.url}")
        return self

    async def check(self):
        logger.info("Checking ComfyUI object_info")
        self._obj_infos = await self._request_get(
            f"{self.url}/object_info", jsondec=True
        )
        if self._obj_infos is None:
            logger.error("Failed to get object_info")
            return False
        else:
            logger.success("Got object_info")
            return True

    def getBackendConfig(self):
        return self._obj_infos

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

    async def _queue_prompt(self, prompt, client_id):
        url = f"{self.url}/prompt"
        data = {"prompt": prompt, "client_id": client_id}
        logger.debug("Sending prompt")
        res = await self._request_post(url, data)
        logger.debug("Got prompt response")
        return res

    async def _get_images(self, ws, prompt, client_id):
        prompt_id = (await self._queue_prompt(prompt, client_id))["prompt_id"]
        logger.debug(f"Got prompt_id: {prompt_id}")
        allb64 = {}

        async for message in ws:
            try:
                message_data = json.loads(message)
                if message_data["type"] == "progress" and message_data.get("data"):
                    pass
                elif message_data["type"] == "executing" and message_data.get("data"):
                    data = message_data["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break
                elif message_data["type"] == "ntlb64part" and message_data.get("data"):
                    mdata = message_data["data"]
                    nodelabel = mdata["nodelabel"]
                    img_idx = mdata["img_idx"]
                    part_idx = mdata["part_idx"]
                    part_b64 = mdata["part_b64"]

                    if nodelabel not in allb64:
                        allb64[nodelabel] = {}
                    if img_idx not in allb64[nodelabel]:
                        allb64[nodelabel][img_idx] = {}

                    allb64[nodelabel][img_idx][part_idx] = part_b64
            except Exception as ex:
                logger.error(f"Error processing message: {ex}")
                continue

        logger.debug("Got all base64 parts")
        output_images = self._merge_base64_to_pil(allb64)
        logger.debug("Merged base64 parts to images")
        return output_images

    def _is_continuous(self, img_data):
        keys = sorted(img_data.keys())
        return keys == list(range(len(keys)))

    def _merge_base64_to_pil(self, allb64):
        result = {}
        for node, node_data in allb64.items():
            result[node] = []
            for img_index, img_data in node_data.items():
                if not self._is_continuous(img_data):
                    logger.warning(
                        f"Skipping non-continuous image: node_{node}_image_{img_index}"
                    )
                    continue

                full_b64 = "".join(value for _, value in sorted(img_data.items()))

                try:
                    img_bytes = base64.b64decode(full_b64)
                    img = Image.open(io.BytesIO(img_bytes))
                    result[node].append(img)
                    logger.info(f"Processed image: node_{node}_image_{img_index}")
                except Exception as e:
                    logger.error(
                        f"Error processing image: node_{node}_image_{img_index}. Error: {str(e)}"
                    )

        return result

    async def free_memory(self):
        url = f"{self.url}/free"
        logger.info("Ask for Freeing memory")
        return await self._request_post(url, {"free_memory": True}, False)

    async def draw(self, config: dict) -> List[Image.Image]:
        try:
            modified_api_base = re.sub(r"^https?://|/$", "", self.url)
            wsurl = f"ws://{modified_api_base}/ws?clientId={self._client_id}"

            drawconfig = config["config"]
            outputconfig = config["outputs"]
            outputpath = None
            outputtype = None
            fps = None

            for ocfg in outputconfig:
                if ocfg["ctype"] == "IMAGES":
                    outputpath = ocfg["path"][0]
                    outputtype = ocfg["ctype"]
                    break
                if ocfg["ctype"] == "VIDEO":
                    outputpath = ocfg["path"][0]
                    outputtype = ocfg["ctype"]
                    fps = ocfg["fps"]
                    break

            async with websocket_connect(wsurl) as ws:
                node_outputs = await self._get_images(ws, drawconfig, self._client_id)
                images = fetchImgsFromNode(outputpath, node_outputs, ftype=2)

                return AiDrawResult(
                    aitype=(
                        AiDrawResultType.IMAGE
                        if outputtype == "IMAGES"
                        else AiDrawResultType.VIDEO
                    ),
                    result=images,
                    videofps=fps,
                )

        except Exception as ex:
            logger.error(f"Error in draw method: {ex}")
            raise


ComfySDKInstance = ComfyUISDK()
