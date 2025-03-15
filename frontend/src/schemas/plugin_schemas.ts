// 基本类型定义
export type PropVarType = 'Value' | 'Ref' | 'VModel'

export interface PropVar {
  Type: PropVarType
  Data: any
}

export interface BaseComponent {
  Type: string
  Props: Record<string, PropVar>
  Slots?: Record<string, any>
}

// 插件相关类型
export interface VFPluginSetting {
  Execute: string
}

export interface VFPlugin {
  Type: string
  Name: string
  Description: string
  Execute: string
  Setting: VFPluginSetting
}

export interface VFUIPlugin {
  Type: string
  Name: string
  Component: string | BaseComponent
}

export interface VFProvider {
  Provider: string
  Version: string
  Description: string
  Author: string
  Icon?: string
  ProviderSetting: VFPluginSetting
  Plugins: VFPlugin[]
  UIPlugins: VFUIPlugin[]
}
