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

export type ComponentProp = ValueProp | VBindProp | VModelProp

export interface VForProps {
  items: ComponentProp
  itemLabel: string
  indexLabel: string
  template: BaseComponent
}

export interface BaseComponent {
  Type: string
  Props?: Record<string, ComponentProp | VForProps>
  Slots?: Record<string, BaseComponent | BaseComponent[]>
  IfCondition?: Condition
}

export type Condition =
  | CompareCondition
  | LogicalCondition
  | ValueCondition<boolean>
  | VBindCondition

export interface CompareCondition {
  Type: 'Compare'
  Left: Condition
  Operator: '==' | '===' | '!=' | '!==' | '>' | '<' | '>=' | '<='
  Right: Condition
}

export interface LogicalCondition {
  Type: 'Logical'
  Operator: 'AND' | 'OR'
  Conditions: Condition[]
}

export interface ValueCondition<T> {
  Type: 'Value'
  Data: T
}

export interface VBindCondition {
  Type: 'VBind'
  Data: (string | number)[]
}

// 插件相关类型
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
