from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    TEXT,
    DECIMAL,
    ForeignKey,
    TypeDecorator,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.db.base import Base
import json


class BigJSONType(TypeDecorator):
    """自定义类型，用于处理大 JSON 数据"""

    impl = TEXT  # 使用 TEXT 类型存储
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """插入数据时，将 dict 序列化为 JSON 字符串"""
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return None

    def process_result_value(self, value, dialect):
        """读取数据时，将 JSON 字符串反序列化为 dict"""
        if value is not None:
            return json.loads(value)
        return None


class FAWorkflowModel(Base):
    __tablename__ = "fa_workflow"

    wid: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    curVFlow: Mapped[Optional[dict]] = mapped_column(BigJSONType)
    lastModified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # 反向关系到历史记录
    releasedVFlows: Mapped[List[FAReleasedWorkflowModel]] = relationship(
        "FAReleasedWorkflowModel",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )


class FAReleasedWorkflowModel(Base):
    __tablename__ = "fa_released_workflow"

    rwid: Mapped[str] = mapped_column(String(255), primary_key=True)
    vflow: Mapped[dict] = mapped_column(BigJSONType)
    releaseTime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(TEXT)
    # 修改: 添加 ondelete="CASCADE"
    wid: Mapped[str] = mapped_column(
        String(255), ForeignKey("fa_workflow.wid", ondelete="CASCADE"), nullable=False
    )
    # 反向关系
    workflow: Mapped["FAWorkflowModel"] = relationship(
        "FAWorkflowModel", back_populates="releasedVFlows"
    )
    # 定义复合索引
    __table_args__ = (Index("idx_fa_released_workflow_wid_rwid", "wid", "rwid"),)
    pass


class FANodeCacheModel(Base):
    __tablename__ = "fa_node_cache"

    cid: Mapped[str] = mapped_column(String(255), primary_key=True)
    nid: Mapped[str] = mapped_column(String(255), primary_key=True)
    oriid: Mapped[str] = mapped_column(String(255))
    data: Mapped[dict] = mapped_column(BigJSONType, nullable=False)
    ntype: Mapped[str] = mapped_column(String(255))
    parentNode: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    runStatus: Mapped[str] = mapped_column(String(255))

    # 修改: 添加 ondelete="CASCADE"
    wid: Mapped[str] = mapped_column(
        String(255), ForeignKey("fa_workflow.wid", ondelete="CASCADE"), nullable=False
    )
    # 定义复合索引
    __table_args__ = (Index("idx_fa_node_cache_wid_cid_nid", "wid", "cid", "nid"),)
    pass


class FANodeConfigStoreModel(Base):
    __tablename__ = "fa_node_config_store"

    NodeName: Mapped[str] = mapped_column(String(255), primary_key=True)
    NodeConfig: Mapped[dict] = mapped_column(BigJSONType, nullable=False)
    pass
