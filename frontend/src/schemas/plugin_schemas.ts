import { type CodeEditorLanguage } from '@/components/nodes/VFNodeInterface'

// 特殊定义 =====================================================================

// 路径定义
export const THIS_NODE_DATA = '@THIS_NODE_DATA@' as const
export const CONTEXT_FUNCTION = '@CONTEXT_FUNCTION@' as const
export const VFOR_DATA = '@VFOR_DATA@' as const
export const NODE_CONFIG = '@NODE_CONFIG@' as const
export const PAYLOADS_ID = '@PAYLOADS_ID@' as const
// 连接项定义，路径为[CONNECT_*, <Handle Type>, <Handle Id>], 如果没有<Handle Id>则默认获取所有<Handle Id>
export const CONNECT_DATA = '@CONNECT_DATA@' as const
export const CONNECT_DATA_HANDLE = '@CONNECT_DATA_HANDLE@' as const
export const CONNECT_DATA_TO_SELECT = '@CONNECT_DATA_TO_SELECT@' as const
// 类型定义
export const TYPE_VFOR = '@VFOR@' as const
export const TYPE_VALUE = '@VALUE@' as const
export const TYPE_VBIND = '@VBIND@' as const
export const TYPE_VMODEL = '@VMODEL@' as const
export const TYPE_CONDITION_COMPARE = '@CONDITION_COMPARE@' as const
export const TYPE_CONDITION_LOGICAL = '@CONDITION_LOGICAL@' as const
export const TYPE_CONDITION_DIRECT = '@CONDITION_DIRECT@' as const
export const TYPE_CONDITION_VBIND = '@CONDITION_VBIND@' as const
export const TYPE_CONDITION_VALUE = '@CONDITION_VALUE@' as const
export enum FunctionPropType {
  ADDITEM = '@ADDITEM@',
  REMOVEITEM = '@REMOVEITEM@',
  APPENDITEM = '@APPENDITEM@',
  ADDRESULT2OUT = '@ADDRESULT2OUT@',
  REMOVERESULT4OUT = '@REMOVERESULT4OUT@',
  OPENEDITOR = '@OPENEDITOR@',
}
export enum PropVarType {
  Value = '@VALUE@',
  VBind = '@VBIND@',
  VModel = '@VMODEL@',
  Function = '@FUNCTION@',
}
// =============================================================================
// 接口定义
export interface PropVarBase {
  Type: PropVarType
}

export interface ValueProp<T = any> extends PropVarBase {
  Type: PropVarType.Value
  Data: T
}

export interface VBindProp extends PropVarBase {
  Type: PropVarType.VBind
  Data: (string | number)[]
}

export interface VModelProp extends PropVarBase {
  Type: PropVarType.VModel
  Data: (string | number)[]
}

export interface FunctionProp extends PropVarBase {
  Type: PropVarType.Function
  Func: FunctionPropType
  Arg: {
    DstPath?: (string | number)[]
    ItemKey?: ReadOnlyPropVar
    ItemValue?: any
    HandleId?: string
    Result?: any
    ResultId?: ReadOnlyPropVar
    Language?: CodeEditorLanguage
  }
}

export type PropVar = ValueProp | VBindProp | VModelProp | FunctionProp
export type ReadOnlyPropVar = ValueProp | VBindProp
export type BaseComponent = NormalComponent | SpanComponent | ForLoopComponent

// 普通组件类型
export interface NormalComponent {
  Type: string
  Props?: Record<string, PropVar>
  Slots?: Record<string, BaseComponent | BaseComponent[]>
  IfCondition?: Condition
}

// 特殊绑定组件 (@Value@/@VBind@)
export interface SpanComponent {
  Type: typeof TYPE_VALUE | typeof TYPE_VBIND
  Data: (string | number)[] | any
  IfCondition?: Condition
  // 特殊绑定组件不允许有子组件
  Slots?: never
  Props?: never
  Items?: never
  Template?: never
}

// 循环组件 (@VFOR@)
export interface ForLoopComponent {
  Type: typeof TYPE_VFOR
  Items: ReadOnlyPropVar
  ItemLabel: string
  IndexLabel: string
  Template: BaseComponent | BaseComponent[]
  IfCondition?: Condition
  // 特殊绑定组件不允许有子组件
  Slots?: never
  Props?: never
}

// 条件判断系统
export type Condition = CompareCondition | LogicalCondition | DirectCondition

// 直接条件（修改为与Python模型一致的结构）
export interface DirectCondition {
  Type: typeof TYPE_CONDITION_DIRECT
  Condition: ReadOnlyPropVar
}

// 比较条件
export interface CompareCondition {
  Type: typeof TYPE_CONDITION_COMPARE
  Left: ReadOnlyPropVar
  Operator: '==' | '!=' | '>' | '<' | '>=' | '<='
  Right: ReadOnlyPropVar
}

// 逻辑组合条件
export interface LogicalCondition {
  Type: typeof TYPE_CONDITION_LOGICAL
  Operator: 'AND' | 'OR'
  Conditions: Condition[]
}

// 插件系统保持不变
export interface VFPluginSetting {
  Execute: string
}

export interface VFPlugin {
  Type: string
  Name: string
  Label: string
  Description: string
  Execute: string
  Setting: VFPluginSetting
  CreateInfo: any
  NeedOptions: any
}

export interface VFUIPlugin {
  Type: string
  Name: string
  Component: BaseComponent
}

export interface VFProvider {
  Provider: string
  Label: string
  Version: string
  Description: string
  Author: string
  Icon?: string
  ProviderSetting: VFPluginSetting
  Plugins: VFPlugin[]
  UIPlugins: VFUIPlugin[]
}
