import type {
  VFNodeContentData,
  VFNodeContents,
  VFNodeHandleData,
  VFNodeHandle,
  VFNodeConnections,
  VFNodeAttaching,
  VFNodeAttachedNode,
  VFNodePadding,
  VFNodeSize,
  VFNodeNesting,
  VFNodeState,
  VFNodeConfig,
  BaseVFNodeData,
  AttachedVFNodeData,
  NestedVFNodeData,
  VFNodeData,
} from '@/components/nodes/VFNodeInterface'

import {
  VFNodeConnectionDataType,
  VFNodeConnectionDataAttachedType,
  VFNodeConnectionType,
  VFNodeFlag,
  VFNodeAttachingPos,
  VFNodeAttachingType,
} from '@/components/nodes/VFNodeInterface'

import { getUuid } from '@/utils/tools'

class VFNode implements BaseVFNodeData {
  // 基础必选属性
  ntype: string
  vtype: string
  flag: number
  label: string
  placeholderlabel: string
  size: VFNodeSize
  connections: VFNodeConnections
  payloads: VFNodeContents
  results: VFNodeContents
  state: VFNodeState
  config: VFNodeConfig

  // 可选特性
  min_size?: VFNodeSize
  attaching?: VFNodeAttaching
  nesting?: VFNodeNesting

  constructor(ntype: string, vtype: string, label: string) {
    this.ntype = ntype
    this.vtype = vtype
    this.label = label
    this.placeholderlabel = label
    this.flag = 0
    this.size = { width: -1, height: -1 }

    // 初始化所有必选属性
    this.connections = this.createDefaultConnections()
    this.payloads = this.createDefaultContents()
    this.results = this.createDefaultContents()
    this.state = this.createDefaultState()
    this.config = this.createDefaultConfig()
  }

  // 初始化方法 ====================================================
  private createDefaultConnections(): VFNodeConnections {
    return {
      self: { self: { label: 'self', data: {} } },
      attach: { attach: { label: 'attach', data: {} } },
      next: { next: { label: 'next', data: {} } },
      inputs: {},
      outputs: {},
      callbackUsers: {},
      callbackFuncs: {},
    }
  }

  private createDefaultContents(): VFNodeContents {
    return { byId: {}, order: [] }
  }

  private createDefaultState(): VFNodeState {
    return {
      status: 'Default',
      copy: {},
      copyCount: { Running: 0, Success: 0, Error: 0 },
      validation_errors: [],
    }
  }

  private createDefaultConfig(): VFNodeConfig {
    return { outputsUIType: '' }
  }

  // 类型初始化方法 ================================================
  initAsNestedNode(tag: string | null): this & NestedVFNodeData {
    this.flag |= VFNodeFlag.isNested
    this.min_size = { width: 200, height: 200 }
    this.nesting = {
      tag,
      pad: { top: 60, bottom: 40, left: 60, right: 60, gap: 0 },
      attached_pad: { top: 30, bottom: 25, left: 17, right: 17, gap: 20 },
      attached_nodes: {},
    }
    return this as this & NestedVFNodeData
  }

  initAsAttachedNode(
    type: VFNodeAttachingType,
    pos: [VFNodeAttachingPos, number, VFNodeAttachingPos, number],
    label: string,
  ): this & AttachedVFNodeData {
    this.flag |= VFNodeFlag.isAttached
    this.attaching = { type, pos, label }
    return this as this & AttachedVFNodeData
  }

  // 类型守卫 ======================================================
  isAttachedNode(): this is AttachedVFNodeData {
    return (this.flag & VFNodeFlag.isAttached) !== 0
  }

  isNestedNode(): this is NestedVFNodeData {
    return (this.flag & VFNodeFlag.isNested) !== 0
  }

  // 属性操作方法 ==================================================
  setLabel(label: string): this {
    this.label = label
    return this
  }

  setSize(width: number, height: number): this {
    const minWidth = this.isNestedNode() ? (this.min_size?.width ?? 0) : 0
    const minHeight = this.isNestedNode() ? (this.min_size?.height ?? 0) : 0
    this.size = {
      width: Math.max(width, minWidth),
      height: Math.max(height, minHeight),
    }
    return this
  }

  setNodeFlag(flag: VFNodeFlag): this {
    this.flag = flag
    return this
  }

  // 连接点操作 ====================================================
  addHandle(connectType: VFNodeConnectionType, handleId: string, label?: string): this {
    this.connections[connectType][handleId] = {
      label: label || handleId,
      data: {},
    }
    return this
  }

  rmHandle(connectType: VFNodeConnectionType, handleId: string): this {
    if (this.connections[connectType][handleId]) {
      delete this.connections[connectType][handleId]
    }
    return this
  }

  addHandleData(
    connectType: VFNodeConnectionType,
    handleId: string,
    data: VFNodeHandleData,
    did?: string | null,
  ): string {
    const handle = this.connections[connectType][handleId]
    if (!handle) throw new Error(`Handle ${handleId} not found in ${connectType}`)

    const dataId = did || getUuid()
    handle.data[dataId] = data
    return dataId
  }

  rmHandleData(connectType: VFNodeConnectionType, handleId: string, did: string): this {
    const handle = this.connections[connectType][handleId]
    if (handle?.data[did]) {
      delete handle.data[did]
    }
    return this
  }

  // 数据内容操作 ==================================================
  addPayload(content: Omit<VFNodeContentData, 'hid' | 'did'>, pid?: string): string {
    const id = pid || getUuid()
    this.payloads.byId[id] = { ...content, hid: '', did: '' }
    this.payloads.order.push(id)
    return id
  }

  rmPayload(pid: string): this {
    const payload = this.payloads.byId[pid]
    if (!payload) return this
    delete this.payloads.byId[pid]
    this.payloads.order.splice(this.payloads.order.indexOf(pid), 1)
    return this
  }

  addResult(content: Omit<VFNodeContentData, 'hid' | 'did'>, rid?: string): string {
    const id = rid || getUuid()
    this.results.byId[id] = { ...content, hid: '', did: '' }
    this.results.order.push(id)
    return id
  }

  rmResult(rid: string): this {
    const result = this.results.byId[rid]
    if (!result) return this
    delete this.results.byId[rid]
    this.results.order.splice(this.results.order.indexOf(rid), 1)
    return this
  }

  addResultWithConnection(
    content: Omit<VFNodeContentData, 'hid' | 'did'>,
    handleId: string,
    rid: string | null = null,
    did: string | null = null,
  ): string {
    if (!this.connections.outputs[handleId]) {
      this.addHandle(VFNodeConnectionType.outputs, handleId)
    }

    const _rid = rid || getUuid()
    const _did = this.addHandleData(
      VFNodeConnectionType.outputs,
      handleId,
      {
        type: VFNodeConnectionDataType.FromInner,
        path: ['results', _rid],
        useid: [],
      },
      did,
    )

    this.results.byId[_rid] = { ...content, hid: handleId, did: _did }
    this.results.order.push(_rid)
    return _rid
  }

  rmResultWithConnection(rid: string): this {
    const result = this.results.byId[rid]
    if (!result) return this
    const handleId = result.hid
    const dataId = result.did
    if (!dataId || !handleId) return this

    this.rmHandleData(VFNodeConnectionType.outputs, handleId, dataId)
    delete this.results.byId[rid]
    this.results.order.splice(this.results.order.indexOf(rid), 1)
    return this
  }

  // 嵌套节点操作 ==================================================
  addAttachedNode(type: VFNodeConnectionDataAttachedType): this {
    if (!this.isNestedNode()) {
      throw new Error('Cannot add attached node to non-nested node')
    }

    this.nesting!.attached_nodes[type] = { nid: null }
    return this
  }

  // 状态管理 ======================================================
  updateStatus(status: 'Running' | 'Success' | 'Error'): this {
    this.state.status = status
    this.state.copyCount[status] += 1
    return this
  }

  resetState(): this {
    this.state = this.createDefaultState()
    return this
  }

  // 配置操作 ======================================================
  setOutputsUIType(uitype: string): this {
    this.config.outputsUIType = uitype
    return this
  }
}
export function createVFNodeFromData(data: VFNodeData): VFNode {
  // 使用基础属性创建实例
  const node = new VFNode(data.ntype, data.vtype, data.label)

  // 填充其他必选属性
  node.flag = data.flag
  node.placeholderlabel = data.placeholderlabel
  node.size = data.size
  node.connections = data.connections
  node.payloads = data.payloads
  node.results = data.results
  node.state = data.state
  node.config = data.config

  // 处理附属节点特性
  if ('attaching' in data) {
    node.attaching = data.attaching
  }

  // 处理嵌套节点特性
  if ('nesting' in data) {
    const nestedData = data as NestedVFNodeData
    node.min_size = nestedData.min_size
    node.nesting = nestedData.nesting
  }

  return node
}
export { VFNode }
