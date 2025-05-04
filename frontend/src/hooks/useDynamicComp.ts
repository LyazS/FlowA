import { z } from 'zod'
import {
  h,
  resolveComponent,
  inject,
  computed,
  Fragment,
  type VNode,
  type PropType,
  type ComputedRef,
  ref,
} from 'vue'
import { useVueFlow } from '@vue-flow/core'
import type {
  BaseComponent,
  NormalComponent,
  ForLoopComponent,
  SpanComponent,
  CompareCondition,
  LogicalCondition,
  PropVar,
  ReadOnlyPropVar,
  OperateFunctionProp,
  Condition,
  VBindProp,
  ValueProp,
  VModelProp,
  ReturnFunctionProp,
  AsyncReturnFunctionProp,
} from '@/schemas/plugin_schemas'
import {
  PropVarType,
  FunctionPropType,
  THIS_NODE_DATA,
  NODE_CONFIG_DATA,
  COMPONENT_CONTEXT,
  ARG_CONTEXT,
  // GENERATE_UUID,
  VFOR_DATA,
  CONNECT_DATA,
  CONNECT_DATA_TO_SELECT,
  TYPE_VFOR,
  TYPE_VSPAN,
  TYPE_CONDITION_COMPARE,
  TYPE_CONDITION_LOGICAL,
  TYPE_CONDITION_DIRECT,
  TYPE_CONDITION_VBIND,
  TYPE_CONDITION_VALUE,
  // z schemas ===================
  ValuePropSchema,
  VBindPropSchema,
  VModelPropSchema,
  VOpFuncPropSchema,
  VRetFuncPropSchema,
} from '@/schemas/plugin_schemas'
import {
  DYNAMIC_COMPONENTS_MAP,
  DYNAMIC_FA_COMPONENTS_MAP,
  DYNAMIC_ICONS_MAP,
} from '@/schemas/dynamic_components_map'
import { VFNode, InsertPos } from '@/components/nodes/VFNodeClass'
import {
  selectedNodeId,
  isEditorMode,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { type SelectOption } from 'naive-ui'
import { useNodeUtils, type RefVarItem } from '@/hooks/useNodeUtils'
import {
  type CodeEditorLanguage,
  type VFNodeHandleData,
  VFNodeConnectionType,
  type VFNodeContentData,
} from '@/components/nodes/VFNodeInterface'
import { cloneDeep } from 'lodash'
import { getUuid, handleSelectImage } from '@/utils/tools'

interface DynamicCompInstance {
  resolveVBindDataPath: (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => number | string>,
  ) => ValueProp
  resolveDataPath: (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => (string | number)[]
  getValueByPath: (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => any
  updateValueByPath: (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    value: any,
  ) => void
  addItemByPath: (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    key: string | number,
    value: any,
  ) => void
  appendItemByPath: (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    value: any,
    pos?: InsertPos,
  ) => void
  removeItemByPath: (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    key: string | number,
  ) => void
  addItem2Payload: (
    dataContext: Record<string, any>,
    content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
    pid?: string,
    pos?: InsertPos,
  ) => void
  removeItem4Payload: (dataContext: Record<string, any>, pid: string) => void
  addItem2Result: (
    dataContext: Record<string, any>,
    content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
    rid?: string,
    pos?: InsertPos,
  ) => void
  removeItem4Result: (dataContext: Record<string, any>, rid: string) => void
  addResults2Connect: (
    dataContext: Record<string, any>,
    handleid: string,
    result: any,
    rid: string | null,
    did: string | null,
    pos?: InsertPos,
  ) => void
  removeResults4Connect: (dataContext: Record<string, any>, rid: string) => void
  addHandle: (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    handleLabel?: string,
    pos?: InsertPos,
  ) => void
  removeHandle: (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
  ) => void
  addHandleData: (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    data: VFNodeHandleData,
    dataId?: string,
  ) => void
  removeHandleData: (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    dataId: string,
  ) => void
  openCodeEditor: (resolvePath: (string | number)[], lang: CodeEditorLanguage) => void
  getValueFromROP: (
    dataContext: Record<string, any>,
    prop: ReadOnlyPropVar,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => any
  getValueFromROPAsync: (
    dataContext: Record<string, any>,
    prop: ReadOnlyPropVar,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => Promise<any>
}
let instance: DynamicCompInstance | null = null
export const useDynamicComp = () => {
  if (instance) return instance

  const { updateNodeInternals } = useVueFlow()
  const getNodeConfig = inject<(nid: string) => any>('getNodeConfig')!
  const getConnectionsByArgs = inject<
    (args: string[]) =>
      | string[] // 节点层级-节点数组
      | Record<string, Record<string, string[]>> // 句柄层级-句柄字典
      | RefVarItem[] // 变量层级-变量数组
      | SelectOption[] // 变量层级-变量选项/句柄层级-句柄选项
      | null
  >('getConnectionsByArgs')!

  // 数据路径解析器
  // 数据获取依赖数组第一个元素来决定使用字典
  const resolveVBindDataPath = (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => number | string>,
  ): ValueProp => {
    const resolvePath: (string | number)[] = []
    const path = vbdata.FA_Data__
    for (const element of path) {
      if (element.FA_Type__ === PropVarType.Value) {
        resolvePath.push(element.FA_Data__)
      } else if (element.FA_Type__ === PropVarType.VBind) {
        // 递归解析VBindProp
        const bindValue = resolveVBindDataPath(dataContext, element, tmpFunction)
        resolvePath.push(bindValue.FA_Data__)
      }
    }

    let res
    if (resolvePath[0] === THIS_NODE_DATA) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
    } else if (resolvePath[0] === VFOR_DATA) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[VFOR_DATA])
    } else if (resolvePath[0] === NODE_CONFIG_DATA) {
      const nodeConfig = getNodeConfig(selectedNodeId.value as string)
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], nodeConfig)
    } else if (resolvePath[0] === COMPONENT_CONTEXT) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[COMPONENT_CONTEXT])
    } else if (tmpFunction) {
      if (resolvePath[0] in tmpFunction) {
        res = tmpFunction[resolvePath[0]](resolvePath.slice(1))
      }
    }
    if (typeof res != 'number' || typeof res != 'string') {
      return {
        FA_Type__: PropVarType.Value,
        FA_Data__: res,
      }
    }
    throw new Error(`Unsupported data path: ${resolvePath}`)
  }
  const resolveDataPath = (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ): (string | number)[] => {
    const resolvePath: (string | number)[] = []
    const path = vbdata.FA_Data__
    for (const element of path) {
      if (element.FA_Type__ === PropVarType.Value) {
        resolvePath.push(element.FA_Data__)
      } else if (element.FA_Type__ === PropVarType.VBind) {
        // 递归解析VBindProp
        const bindValue = resolveVBindDataPath(dataContext, element, tmpFunction)
        resolvePath.push(bindValue.FA_Data__)
      }
    }
    return resolvePath
  }
  const getValueByPath = (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => {
    const resolvePath = resolveDataPath(dataContext, vbdata, tmpFunction)

    let res
    if (resolvePath[0] === THIS_NODE_DATA) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
    } else if (resolvePath[0] === VFOR_DATA) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[VFOR_DATA])
    } else if (resolvePath[0] === NODE_CONFIG_DATA) {
      const nodeConfig = getNodeConfig(selectedNodeId.value as string)
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], nodeConfig)
    } else if (resolvePath[0] === COMPONENT_CONTEXT) {
      res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], dataContext[COMPONENT_CONTEXT])
    } else if (resolvePath[0] === CONNECT_DATA) {
      if (resolvePath.length >= 2) {
        res = getConnectionsByArgs(resolvePath.slice(1) as string[])
      }
    } else if (tmpFunction) {
      if (resolvePath[0] in tmpFunction) {
        res = tmpFunction[resolvePath[0]](resolvePath.slice(1))
      }
    }
    return res
  }

  // 数据更新
  const updateValueByPath = (
    dataContext: Record<string, any>,
    vbdata: VBindProp | VModelProp,
    value: any,
  ) => {
    const resolvePath = resolveDataPath(dataContext, vbdata)
    // 根据路径更新值
    const firstKey = resolvePath.shift()!
    if (firstKey === THIS_NODE_DATA) {
      const lastKey = resolvePath.pop()!
      const parent = resolvePath.reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
      if (parent) parent[lastKey] = value
    } else {
      console.error(`Unsupported update path: ${resolvePath}`)
    }
  }

  // Object类型数据添加项
  const addItemByPath = (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    key: string | number,
    value: any,
  ) => {
    // 根据路径添加值
    const firstKey = resolvePath.shift()!
    if (firstKey === THIS_NODE_DATA) {
      const parent = resolvePath.reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
      if (parent) {
        parent[key] = value
        return
      }
    }
    console.error(`Unsupported add path: ${resolvePath}`)
  }
  // Object|Array类型数据删除项
  const removeItemByPath = (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    key: string | number,
  ) => {
    // 根据路径删除值
    const firstKey = resolvePath.shift()!
    if (firstKey === THIS_NODE_DATA) {
      const parent = resolvePath.reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
      if (parent) {
        if (Array.isArray(parent) && typeof key === 'number') {
          parent.splice(key as number, 1)
          return
        } else if (typeof parent === 'object') {
          delete parent[key]
          return
        }
      }
    }
    console.error(`Unsupported delete path: ${resolvePath}`)
  }

  // Array类型数据添加项
  const appendItemByPath = (
    dataContext: Record<string, any>,
    resolvePath: (string | number)[],
    value: any,
    pos?: InsertPos,
  ) => {
    // 根据路径插入值
    const firstKey = resolvePath.shift()!
    if (firstKey === THIS_NODE_DATA) {
      const parent = resolvePath.reduce((acc, key) => acc?.[key], dataContext[THIS_NODE_DATA])
      if (parent) {
        if (pos === InsertPos.Start) parent.unshift(value)
        else parent.push(value)
        return
      }
    }
    console.error(`Unsupported append path: ${resolvePath}`)
  }

  // 添加Payload
  const addItem2Payload = (
    dataContext: Record<string, any>,
    content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
    pid?: string,
    pos?: InsertPos,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.addPayload(content, pid, pos)
      return
    }
    console.error(`addItem2Payload error`)
  }

  // 删除Payload
  const removeItem4Payload = (dataContext: Record<string, any>, pid: string) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.rmPayload(pid)
      return
    }
    console.error(`Unsupported remove path: ${pid}`)
  }

  // 添加Result
  const addItem2Result = (
    dataContext: Record<string, any>,
    content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
    rid?: string,
    pos?: InsertPos,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.addResult(content, rid, pos)
      return
    }
    console.error(`addItem2Result error`)
  }

  // 删除Result
  const removeItem4Result = (dataContext: Record<string, any>, rid: string) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.rmResult(rid)
      return
    }
    console.error(`Unsupported remove path: ${rid}`)
  }

  // Results添加项进Connect
  const addResults2Connect = (
    dataContext: Record<string, any>,
    handleid: string,
    result: any,
    rid: string | null = null,
    did: string | null = null,
    pos?: InsertPos,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.addResultWithConnection(result, handleid, rid, did, pos)
      return
    }
    console.error('Unsupported append path')
  }
  // 从Connect删除Results
  const removeResults4Connect = (dataContext: Record<string, any>, rid: string) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.rmResultWithConnection(rid)
      return
    }
    console.error('Unsupported remove path')
  }

  // 添加Handle
  const addHandle = (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    handleLabel?: string,
    pos?: InsertPos,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.addHandle(handleType, handleId, handleLabel, pos)
      if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
      return
    }
    console.error('Unsupported add handle')
  }
  // 删除Handle
  const removeHandle = (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.rmHandle(handleType, handleId)
      if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
      return
    }
    console.error('Unsupported remove handle')
  }
  // 添加Handle数据
  const addHandleData = (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    data: VFNodeHandleData,
    dataId?: string,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.addHandleData(handleType, handleId, data, dataId)
      return
    }
    console.error('Unsupported add handle data')
  }

  // 删除Handle数据
  const removeHandleData = (
    dataContext: Record<string, any>,
    handleType: VFNodeConnectionType,
    handleId: string,
    dataId: string,
  ) => {
    const nodedata = dataContext[THIS_NODE_DATA] as VFNode
    if (nodedata) {
      nodedata.rmHandleData(handleType, handleId, dataId)
      return
    }
    console.error('Unsupported remove handle data')
  }

  // 打开编辑器
  const openCodeEditor = (resolvePath: (string | number)[], lang: CodeEditorLanguage) => {
    // 根据路径打开编辑器
    const firstKey = resolvePath.shift()!
    if (firstKey === THIS_NODE_DATA) {
      CodeEditorPath.value = ['data', ...resolvePath]
      CodeEditorLangType.value = lang
      isShowCodeEditor.value = true
    }
  }

  // 获取ReadOnlyPropVar的值
  const getValueFromROP = (
    dataContext: Record<string, any>,
    prop: ReadOnlyPropVar,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => {
    switch (prop.FA_Type__) {
      case PropVarType.Value: {
        return prop.FA_Data__
      }
      case PropVarType.VBind: {
        return getValueByPath(dataContext, prop, tmpFunction)
      }
      case PropVarType.ReturnFunc: {
        const prop_Function = (prop as ReturnFunctionProp).FA_Func__
        let func: CallableFunction | null = null
        if (prop_Function.Func === FunctionPropType.GENERATEUUID) {
          func = getUuid
        } else if (prop_Function.Func === FunctionPropType.FORMATSTRING) {
          func = () => {
            const { FString, Args } = prop_Function.Arg
            const args: Record<string, any> = {}
            for (const [key, propvar] of Object.entries(Args)) {
              args[key] = getValueFromROP(dataContext, propvar, tmpFunction)
            }
            return FString.replace(/\{\{(\w+)\}\}/g, (match, key) => {
              return args[key] || ''
            })
          }
        }
        if (func) {
          return func()
        }
      }
      default:
        return null
    }
  }

  const getValueFromROPAsync = async (
    dataContext: Record<string, any>,
    prop: ReadOnlyPropVar,
    tmpFunction?: Record<string, (args: (string | number)[]) => any>,
  ) => {
    switch (prop.FA_Type__) {
      case PropVarType.AReturnFunc: {
        const prop_Function = (prop as AsyncReturnFunctionProp).FA_Func__
        let func: CallableFunction | null = null
        if (prop_Function.Func === FunctionPropType.UPLOADIMAGE) {
          func = handleSelectImage
        }
        if (func) {
          return await func()
        }
      }
      default:
        return getValueFromROP(dataContext, prop, tmpFunction)
    }
  }

  instance = {
    resolveVBindDataPath,
    resolveDataPath,
    getValueByPath,
    updateValueByPath,
    addItemByPath,
    appendItemByPath,
    removeItemByPath,
    addItem2Payload,
    removeItem4Payload,
    addItem2Result,
    removeItem4Result,
    addResults2Connect,
    removeResults4Connect,
    addHandle,
    removeHandle,
    addHandleData,
    removeHandleData,
    openCodeEditor,
    getValueFromROP,
    getValueFromROPAsync,
  }

  return instance
}
