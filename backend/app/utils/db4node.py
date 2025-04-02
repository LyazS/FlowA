from typing import Any
from sqlalchemy import select, update, exc, exists, delete
from app.db.session import get_db_ctxmgr
from app.models.fastore import FANodeConfigStoreModel


async def loadNodeConfig(node_name: str):
    async with get_db_ctxmgr() as db:
        stmt = select(exists().where(FANodeConfigStoreModel.NodeName == node_name))
        db_result = await db.execute(stmt)
        db_exists = db_result.scalar()
        if db_exists:
            stmt = select(FANodeConfigStoreModel.NodeConfig).where(
                FANodeConfigStoreModel.NodeName == node_name
            )
            db_result = await db.execute(stmt)
            node_config = db_result.scalars().first()
            return True, node_config
        else:
            return False, None
    pass


async def setNodeConfig(node_name: str, node_config: dict):
    async with get_db_ctxmgr() as db:
        stmt = select(exists().where(FANodeConfigStoreModel.NodeName == node_name))
        db_result = await db.execute(stmt)
        db_exists = db_result.scalar()
        if db_exists:
            stmt = (
                update(FANodeConfigStoreModel)
                .where(FANodeConfigStoreModel.NodeName == node_name)
                .values(NodeConfig=node_config)
            )
            await db.execute(stmt)
        else:
            stmt = FANodeConfigStoreModel(NodeName=node_name, NodeConfig=node_config)
            db.add(stmt)
        await db.commit()
    pass


async def deleteNodeConfig(node_name: str):
    async with get_db_ctxmgr() as db:
        stmt = delete(FANodeConfigStoreModel).where(
            FANodeConfigStoreModel.NodeName == node_name
        )
        await db.execute(stmt)
        await db.commit()
    pass
