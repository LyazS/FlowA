enum VFNodeConnectionDataType {
  FromOuter = 'FromOuter',
  FromAttached = 'FromAttached',
  FromParent = 'FromParent',
  FromInner = 'FromInner',
}

enum VFNodeConnectionDataAttachedType {
  attached_node_input = 'attached_node_input',
  attached_node_callbackUser = 'attached_node_callbackUser',
  attached_node_output = 'attached_node_output',
  attached_node_next = 'attached_node_next',
  attached_node_callbackFunc = 'attached_node_callbackFunc',
  attached_node_break = 'attached_node_break',
}
enum VFNodeConnectionType {
  self = 'self',
  attach = 'attach',
  next = 'next',
  inputs = 'inputs',
  outputs = 'outputs',
  callbackUsers = 'callbackUsers',
  callbackFuncs = 'callbackFuncs',
}
enum VFNodeFlag {
  isNested = 0x01,
  isAttached = 0x02,
  isTask = 0x04,
  isPassive = 0x08,
}
enum VFNodeAttachingType {
  input = 'input',
  output = 'output',
  callbackFunc = 'callbackFunc',
  callbackUser = 'callbackUser',
  // next = 'next',
}
enum VFNodeAttachingPos {
  top = 'top',
  bottom = 'bottom',
  left = 'left',
  right = 'right',
  center = 'center',
}

type CodeEditorLanguage = 'python' | 'json' | 'django' | 'text'

interface VFNodeContentDataConfig {
  language?: CodeEditorLanguage
  ref?: string
}
interface VFNodeContentData {
  label: string
  type: string
  key: string
  data: any
  config?: VFNodeContentDataConfig
  hid?: string
  did?: string
  uitype?: string
}

interface VFNodeContents {
  byId: Record<string, VFNodeContentData>
  order: string[]
}

interface VFNodeHandleData {
  type: VFNodeConnectionDataType
  inputKey?: string
  atype?: VFNodeConnectionDataAttachedType
  path?: (string | number)[]
  useid?: string[]
}

interface VFNodeHandle {
  label: string
  data: Record<string, VFNodeHandleData>
}

type VFNodeConnections = {
  // 连接类型：handleID：{handle标签，handle数据}
  [key in VFNodeConnectionType]: Record<string, VFNodeHandle>
}

interface VFNodeAttaching {
  type: VFNodeAttachingType
  pos: [VFNodeAttachingPos, number, VFNodeAttachingPos, number]
  label: string
}

interface VFNodeAttachedNode {
  nid: string | null
}

interface VFNodePadding {
  top: number
  bottom: number
  left: number
  right: number
  gap: number
}

interface VFNodeSize {
  width: number
  height: number
}

interface VFNodeNesting {
  tag: string | null
  pad: VFNodePadding
  attached_pad: VFNodePadding
  attached_nodes: Partial<Record<VFNodeConnectionDataAttachedType, VFNodeAttachedNode>>
}

interface VFNodeState {
  status: string
  copy: Record<string, any>
  copyCount: {
    Running: number
    Success: number
    Error: number
  }
  validation_errors: string[]
}

interface VFNodeConfig {
  outputsUIType: string
}
// 基础节点接口（所有节点的共有属性）
interface BaseVFNodeData {
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
}

// 附属节点接口
interface AttachedVFNodeData extends BaseVFNodeData {
  attaching: VFNodeAttaching
}

// 嵌套节点接口
interface NestedVFNodeData extends BaseVFNodeData {
  min_size: VFNodeSize
  nesting: VFNodeNesting
}

// 组合成联合类型
type VFNodeData = BaseVFNodeData | AttachedVFNodeData | NestedVFNodeData

// 类型守卫
function isAttachedNode(node: VFNodeData): node is AttachedVFNodeData {
  return (node.flag & VFNodeFlag.isAttached) !== 0
}

function isNestedNode(node: VFNodeData): node is NestedVFNodeData {
  return (node.flag & VFNodeFlag.isNested) !== 0
}

export type {
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
  CodeEditorLanguage,
}
export {
  VFNodeConnectionDataType,
  VFNodeConnectionDataAttachedType,
  VFNodeConnectionType,
  VFNodeFlag,
  VFNodeAttachingPos,
  VFNodeAttachingType,
  isAttachedNode,
  isNestedNode,
}
