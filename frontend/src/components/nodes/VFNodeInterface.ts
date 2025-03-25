enum VFNodeConnectionDataType {
  FromOuter = 'FromOuter',
  FromAttached = 'FromAttached',
  FromParent = 'FromParent',
  FromInner = 'FromInner',
}

enum VFNodeConnectionType {
  Self = 'Self',
  Attach = 'Attach',
  Inputs = 'Inputs',
  Outputs = 'Outputs',
  CallbackUsers = 'CallbackUsers',
  CallbackFuncs = 'CallbackFuncs',
}
enum VFNodeFlag {
  IsNested = 0x01,
  IsAttached = 0x02,
  IsTask = 0x04,
  IsPassive = 0x08,
}
enum VFNodeAttachingType {
  Input = 'Input',
  Output = 'Output',
  CallbackFunc = 'CallbackFunc',
  CallbackUser = 'CallbackUser',
}
enum VFNodeAttachingPosType {
  Top = 'Top',
  Bottom = 'Bottom',
  Left = 'Left',
  Right = 'Right',
  Center = 'Center',
}

type CodeEditorLanguage = 'python' | 'json' | 'django' | 'text'

interface VFNodeContentDataConfig {
  Language?: CodeEditorLanguage
  Ref?: string
}
interface VFNodeContentData {
  Label: string
  Type: string
  Key: string
  Data: any
  Config?: VFNodeContentDataConfig
  Hid?: string
  Did?: string
  UiType?: string
}

interface VFNodeContents {
  ById: Record<string, VFNodeContentData>
  Order: string[]
}

interface VFNodeHandleDataANode {
  ConnectionType: VFNodeConnectionType
  HandleId: string
}

interface VFNodeHandleData {
  Type: VFNodeConnectionDataType
  InputKey?: string
  ANode?: Record<string, VFNodeHandleDataANode>
  Path?: (string | number)[]
  UseIds?: string[]
}

interface VFNodeHandle {
  Label: string
  Data: Record<string, VFNodeHandleData>
}

type VFNodeConnections = {
  // 连接类型：handleID：{handle标签，handle数据}
  // [key in VFNodeConnectionType]: Record<string, VFNodeHandle>
  Self: Record<string, VFNodeHandle>
  Attach: Record<string, VFNodeHandle>
  Inputs: Record<string, VFNodeHandle>
  Outputs: Record<string, VFNodeHandle>
  CallbackUsers: Record<string, VFNodeHandle>
  CallbackFuncs: Record<string, VFNodeHandle>
}

interface VFNodeAttachingPos {
  XType: VFNodeAttachingPosType
  XOffset: number
  YType: VFNodeAttachingPosType
  YOffset: number
}
interface VFNodeAttaching {
  Type: VFNodeAttachingType
  Pos: VFNodeAttachingPos
  Label: string
}

interface VFNodeAttachedNode {
  Nid: string | null
  NType: string
  // Type: VFNodeAttachingType
  // Pos: VFNodeAttachingPos
  // Label: string
}

interface VFNodePadding {
  Top: number
  Bottom: number
  Left: number
  Right: number
  Gap: number
}

interface VFNodeSize {
  Width: number
  Height: number
}

interface VFNodeNesting {
  Tag: string | null
  Pad: VFNodePadding
  APad: VFNodePadding
  ANodes: Record<string, VFNodeAttachedNode>
}

interface VFNodeState {
  Status: string
  Copy: Record<string, any>
  CopyCount: {
    Running: number
    Success: number
    Error: number
  }
  Errors: string[]
}

interface VFNodeConfig {
  OutputsUiType: string
}
// 基础节点接口（所有节点的共有属性）
interface BaseVFNodeData {
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
}

// 附属节点接口
interface AttachedVFNodeData extends BaseVFNodeData {
  Attaching: VFNodeAttaching
}

// 嵌套节点接口
interface NestedVFNodeData extends BaseVFNodeData {
  MinSize: VFNodeSize
  Nesting: VFNodeNesting
}

// 组合成联合类型
type VFNodeData = BaseVFNodeData | AttachedVFNodeData | NestedVFNodeData

// 类型守卫
function isAttachedNode(node: VFNodeData): node is AttachedVFNodeData {
  return (node.Flag & VFNodeFlag.IsAttached) !== 0
}

function isNestedNode(node: VFNodeData): node is NestedVFNodeData {
  return (node.Flag & VFNodeFlag.IsNested) !== 0
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
  VFNodeAttachingPos,
}
export {
  VFNodeConnectionDataType,
  VFNodeConnectionType,
  VFNodeAttachingPosType,
  VFNodeFlag,
  VFNodeAttachingType,
  isAttachedNode,
  isNestedNode,
}
