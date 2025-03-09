export enum FAProgressRequestType {
  VFlowUI = 'VFlowUI',
  JinJa = 'JinJa',
}

export interface FAWorkflowInfo {
  wid: string
  name: string
  lastModified: string
}

export interface FAReleaseWorkflowInfo {
  rwid: string
  name: string
  description: string
  releaseTime: string
}

export interface FANodeUpdateData<T = any> {
  type: 'overwrite' | 'append' | 'remove' | 'dontcare'
  path?: (string | number)[]
  data?: T
}

export interface SSEResponseData<T = any> {
  nid: string
  oriid: string
  data: FANodeUpdateData<T>[]
}

export interface JinjaRefTriggerData {
  path: string[]
  operation: string
  new_value: any
  old_value: any
}
