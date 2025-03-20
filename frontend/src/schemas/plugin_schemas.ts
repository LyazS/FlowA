// 基本类型定义
export enum PropVarType {
  Value = 'Value',
  VBind = 'VBind',
  VModel = 'VModel',
}

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

export type PropVar = ValueProp | VBindProp | VModelProp

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
  Type: '@Value@' | '@VBind@'
  Data: PropVar
  IfCondition?: Condition
  // 特殊绑定组件不允许有子组件
  Slots?: never
  Props?: never
  Items?: never
  Template?: never
}

// 循环组件 (@FOR@)
export interface ForLoopComponent {
  Type: '@FOR@'
  Items: PropVar
  ItemLabel: string
  IndexLabel: string
  Template: BaseComponent | BaseComponent[]
  IfCondition?: Condition
}

// 条件判断系统
export type Condition = CompareCondition | LogicalCondition | DirectCondition

// 比较条件
export interface CompareCondition {
  Type: 'Compare'
  Left: PropVar
  Operator: '==' | '!=' | '>' | '<' | '>=' | '<='
  Right: PropVar
}

// 逻辑组合条件
export interface LogicalCondition {
  Type: 'Logical'
  Operator: 'AND' | 'OR'
  Conditions: Condition[]
}

// 直接值或绑定
export type DirectCondition = ValueCondition<any> | VBindCondition

export interface ValueCondition<T> {
  Type: 'Value'
  Data: T
}

export interface VBindCondition {
  Type: 'VBind'
  Data: (string | number)[]
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
}

export interface VFUIPlugin {
  Type: string
  Name: string
  Component: string | BaseComponent
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
