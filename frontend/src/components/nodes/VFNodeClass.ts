import { cloneDeep } from 'lodash'
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
  VFNodeAttachingPos,
} from '@/components/nodes/VFNodeInterface'

import {
  VFNodeConnectionDataType,
  VFNodeConnectionType,
  VFNodeFlag,
  VFNodeAttachingType,
} from '@/components/nodes/VFNodeInterface'

import { getUuid } from '@/utils/tools'

class VFNode implements BaseVFNodeData {
  // 基础必选属性
  NType: string
  VType: string
  Flag: number
  Label: string
  PlaceholderLabel: string
  Size: VFNodeSize
  Connections: VFNodeConnections
  Payloads: VFNodeContents
  Results: VFNodeContents
  State: VFNodeState
  Config: VFNodeConfig

  // 可选特性
  MinSize?: VFNodeSize
  Attaching?: VFNodeAttaching
  Nesting?: VFNodeNesting

  constructor(ntype: string, vtype: string, label: string) {
    this.NType = ntype
    this.VType = vtype
    this.Label = label
    this.PlaceholderLabel = label
    this.Flag = 0
    this.Size = { Width: -1, Height: -1 }

    // 初始化所有必选属性
    this.Connections = this.createDefaultConnections()
    this.Payloads = this.createDefaultContents()
    this.Results = this.createDefaultContents()
    this.State = this.createDefaultState()
    this.Config = this.createDefaultConfig()
  }

  // 初始化方法 ====================================================
  private createDefaultConnections(): VFNodeConnections {
    return {
      Self: { Self: { Label: 'Self', Data: {} } },
      Attach: { Attach: { Label: 'Attach', Data: {} } },
      Inputs: {},
      Outputs: {},
      CallbackUsers: {},
      CallbackFuncs: {},
    }
  }

  private createDefaultContents(): VFNodeContents {
    return { ById: {}, Order: [] }
  }

  private createDefaultState(): VFNodeState {
    return {
      Status: 'Default',
      Copy: {},
      CopyCount: { Running: 0, Success: 0, Error: 0 },
      Errors: [],
    }
  }

  private createDefaultConfig(): VFNodeConfig {
    return { OutputsUiType: '' }
  }

  // 类型初始化方法 ================================================
  initAsNestedNode(tag: string | null): this & NestedVFNodeData {
    this.Flag |= VFNodeFlag.IsNested
    this.MinSize = { Width: 200, Height: 200 }
    this.Nesting = {
      Tag: tag,
      Pad: { Top: 60, Bottom: 40, Left: 60, Right: 60, Gap: 0 },
      APad: { Top: 30, Bottom: 25, Left: 17, Right: 17, Gap: 20 },
      ANodes: {},
    }
    return this as this & NestedVFNodeData
  }

  initAsAttachedNode(
    type: VFNodeAttachingType,
    pos: VFNodeAttachingPos,
    label: string,
  ): this & AttachedVFNodeData {
    this.Flag |= VFNodeFlag.IsAttached
    this.Attaching = { Type: type, Pos: pos, Label: label }
    return this as this & AttachedVFNodeData
  }

  // 类型守卫 ======================================================
  isAttachedNode(): this is AttachedVFNodeData {
    return (this.Flag & VFNodeFlag.IsAttached) !== 0
  }

  isNestedNode(): this is NestedVFNodeData {
    return (this.Flag & VFNodeFlag.IsNested) !== 0
  }

  // 属性操作方法 ==================================================
  setLabel(label: string): this {
    this.Label = label
    return this
  }

  setSize(width: number, height: number): this {
    const minWidth = this.isNestedNode() ? (this.MinSize?.Width ?? 0) : 0
    const minHeight = this.isNestedNode() ? (this.MinSize?.Height ?? 0) : 0
    this.Size = {
      Width: Math.max(width, minWidth),
      Height: Math.max(height, minHeight),
    }
    return this
  }

  setNodeFlag(flag: VFNodeFlag): this {
    this.Flag = flag
    return this
  }

  // 连接点操作 ====================================================
  addHandle(connectType: VFNodeConnectionType, handleId: string, label?: string): this {
    this.Connections[connectType][handleId] = {
      Label: label || handleId,
      Data: {},
    }
    return this
  }

  rmHandle(connectType: VFNodeConnectionType, handleId: string): this {
    if (this.Connections[connectType][handleId]) {
      delete this.Connections[connectType][handleId]
    }
    return this
  }

  addHandleData(
    connectType: VFNodeConnectionType,
    handleId: string,
    data: VFNodeHandleData,
    did?: string | null,
  ): string {
    const handle = this.Connections[connectType][handleId]
    if (!handle) throw new Error(`Handle ${handleId} not found in ${connectType}`)

    const dataId = did || getUuid()
    handle.Data[dataId] = data
    return dataId
  }

  rmHandleData(connectType: VFNodeConnectionType, handleId: string, did: string): this {
    const handle = this.Connections[connectType][handleId]
    if (handle?.Data[did]) {
      delete handle.Data[did]
    }
    return this
  }

  // 数据内容操作 ==================================================
  addPayload(content: Omit<VFNodeContentData, 'Hid' | 'Did'>, pid?: string): string {
    const id = pid || getUuid()
    this.Payloads.ById[id] = { ...content, Hid: '', Did: '' }
    this.Payloads.Order.push(id)
    return id
  }

  rmPayload(pid: string): this {
    const payload = this.Payloads.ById[pid]
    if (!payload) return this
    delete this.Payloads.ById[pid]
    this.Payloads.Order.splice(this.Payloads.Order.indexOf(pid), 1)
    return this
  }

  addResult(content: Omit<VFNodeContentData, 'Hid' | 'Did'>, rid?: string): string {
    const id = rid || getUuid()
    this.Results.ById[id] = { ...content, Hid: '', Did: '' }
    this.Results.Order.push(id)
    return id
  }

  rmResult(rid: string): this {
    const result = this.Results.ById[rid]
    if (!result) return this
    delete this.Results.ById[rid]
    this.Results.Order.splice(this.Results.Order.indexOf(rid), 1)
    return this
  }

  addResultWithConnection(
    content: Omit<VFNodeContentData, 'hid' | 'did'>,
    handleId: string,
    rid: string | null = null,
    did: string | null = null,
  ): string {
    if (!this.Connections.Outputs[handleId]) {
      this.addHandle(VFNodeConnectionType.Outputs, handleId)
    }

    const _rid = rid || getUuid()
    const _did = this.addHandleData(
      VFNodeConnectionType.Outputs,
      handleId,
      {
        Type: VFNodeConnectionDataType.FromInner,
        Path: { ContentName: 'Results', ContentId: _rid },
        UseIds: [],
      },
      did,
    )

    this.Results.ById[_rid] = { ...content, Hid: handleId, Did: _did }
    this.Results.Order.push(_rid)
    return _rid
  }

  rmResultWithConnection(rid: string): this {
    const result = this.Results.ById[rid]
    if (!result) return this
    const handleId = result.Hid
    const dataId = result.Did
    if (!dataId || !handleId) return this

    this.rmHandleData(VFNodeConnectionType.Outputs, handleId, dataId)
    delete this.Results.ById[rid]
    this.Results.Order.splice(this.Results.Order.indexOf(rid), 1)
    return this
  }

  // 嵌套节点操作 ==================================================
  addAttachedNode(
    aname: string,
    antype: string,
    // type: VFNodeAttachingType,
    // pos: VFNodeAttachingPos,
    // label: string,
  ): this {
    if (!this.isNestedNode()) {
      throw new Error('Cannot add attached node to non-nested node')
    }

    // this.Nesting!.ANodes[aname] = { Nid: null, Type: type, Pos: pos, Label: label }
    this.Nesting!.ANodes[aname] = { Nid: null, NType: antype }
    return this
  }

  // 状态管理 ======================================================
  updateStatus(status: 'Running' | 'Success' | 'Error'): this {
    this.State.Status = status
    this.State.CopyCount[status] += 1
    return this
  }

  resetState(): this {
    this.State = this.createDefaultState()
    return this
  }

  // 配置操作 ======================================================
  setOutputsUIType(uitype: string): this {
    this.Config.OutputsUiType = uitype
    return this
  }
}
export function createVFNodeFromData(data: VFNodeData): VFNode {
  const cp_data = cloneDeep(data)
  // 使用基础属性创建实例
  const node = new VFNode(cp_data.NType, cp_data.VType, cp_data.Label)

  // 填充其他必选属性
  node.Flag = cp_data.Flag
  node.PlaceholderLabel = cp_data.PlaceholderLabel
  node.Size = cp_data.Size
  node.Connections = cp_data.Connections
  node.Payloads = cp_data.Payloads
  node.Results = cp_data.Results
  node.State = cp_data.State
  node.Config = cp_data.Config

  // 处理附属节点特性
  if ('Attaching' in cp_data) {
    node.Attaching = cp_data.Attaching
  }

  // 处理嵌套节点特性
  if ('Nesting' in cp_data) {
    const nestedData = cp_data as NestedVFNodeData
    node.MinSize = nestedData.MinSize
    node.Nesting = nestedData.Nesting
  }

  return node
}
export { VFNode }
