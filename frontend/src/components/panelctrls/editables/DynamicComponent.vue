<script setup lang="ts">
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
  FunctionProp,
  Condition,
  VBindProp,
  ValueProp,
  VModelProp,
} from '@/schemas/plugin_schemas'
import {
  PropVarType,
  FunctionPropType,
  THIS_NODE_DATA,
  NODE_CONFIG_DATA,
  CONTEXT_FUNCTION,
  CONTEXT_ARG,
  GENERATE_UUID,
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
import { getUuid } from '@/utils/tools'

defineOptions({
  name: 'DynamicComponent',
})
const { updateNodeInternals } = useVueFlow()
const props = defineProps({
  componentData: {
    type: Object as PropType<BaseComponent>,
    required: true,
  },
  dataContext: {
    type: Object as PropType<Record<string, any>>,
    required: true,
  },
})

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
  vbdata: VBindProp | VModelProp,
  tmpFunction?: Record<string, (args: (string | number)[]) => number | string>,
): ValueProp => {
  const resolvePath: (string | number)[] = []
  const path = vbdata.Data
  for (const element of path) {
    if (element.Type === PropVarType.Value) {
      resolvePath.push(element.Data)
    } else if (element.Type === PropVarType.VBind) {
      // 递归解析VBindProp
      const bindValue = resolveVBindDataPath(element, tmpFunction)
      resolvePath.push(bindValue.Data)
    }
  }

  let res
  if (resolvePath[0] === THIS_NODE_DATA) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
  } else if (resolvePath[0] === VFOR_DATA) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[VFOR_DATA])
  } else if (resolvePath[0] === NODE_CONFIG_DATA) {
    const nodeConfig = getNodeConfig(selectedNodeId.value as string)
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], nodeConfig)
  } else if (resolvePath[0] === CONTEXT_FUNCTION) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[CONTEXT_FUNCTION])
  } else if (resolvePath[0] === GENERATE_UUID) {
    res = getUuid()
  } else if (tmpFunction) {
    if (resolvePath[0] in tmpFunction) {
      res = tmpFunction[resolvePath[0]](resolvePath.slice(1))
    }
  }
  if (typeof res != 'number' || typeof res != 'string') {
    return {
      Type: PropVarType.Value,
      Data: res,
    }
  }
  throw new Error(`Unsupported data path: ${resolvePath}`)
}
const resolveDataPath = (
  vbdata: VBindProp | VModelProp,
  tmpFunction?: Record<string, (args: (string | number)[]) => any>,
): (string | number)[] => {
  const resolvePath: (string | number)[] = []
  const path = vbdata.Data
  for (const element of path) {
    if (element.Type === PropVarType.Value) {
      resolvePath.push(element.Data)
    } else if (element.Type === PropVarType.VBind) {
      // 递归解析VBindProp
      const bindValue = resolveVBindDataPath(element, tmpFunction)
      resolvePath.push(bindValue.Data)
    }
  }
  return resolvePath
}
const getValueByPath = (
  vbdata: VBindProp | VModelProp,
  tmpFunction?: Record<string, (args: (string | number)[]) => any>,
) => {
  const resolvePath = resolveDataPath(vbdata, tmpFunction)

  let res
  if (resolvePath[0] === THIS_NODE_DATA) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
  } else if (resolvePath[0] === VFOR_DATA) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[VFOR_DATA])
  } else if (resolvePath[0] === NODE_CONFIG_DATA) {
    const nodeConfig = getNodeConfig(selectedNodeId.value as string)
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], nodeConfig)
  } else if (resolvePath[0] === CONTEXT_FUNCTION) {
    res = resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[CONTEXT_FUNCTION])
  } else if (resolvePath[0] === GENERATE_UUID) {
    res = getUuid()
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
const updateValueByPath = (vbdata: VBindProp | VModelProp, value: any) => {
  const resolvePath = resolveDataPath(vbdata)
  // 根据路径更新值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const lastKey = resolvePath.pop()!
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) parent[lastKey] = value
  } else {
    console.error(`Unsupported update path: ${resolvePath}`)
  }
}

// Object类型数据添加项
const addItemByPath = (resolvePath: (string | number)[], key: string | number, value: any) => {
  // 根据路径添加值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) {
      parent[key] = value
      return
    }
  }
  console.error(`Unsupported add path: ${resolvePath}`)
}
// Object|Array类型数据删除项
const removeItemByPath = (resolvePath: (string | number)[], key: string | number) => {
  // 根据路径删除值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
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
const appendItemByPath = (resolvePath: (string | number)[], value: any) => {
  // 根据路径插入值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) {
      parent.push(value)
      return
    }
  }
  console.error(`Unsupported append path: ${resolvePath}`)
}

// 添加Payload
const addItem2Payload = (
  content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
  pid?: string,
  pos?: InsertPos,
) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addPayload(content, pid, pos)
    return
  }
  console.error(`addItem2Payload error`)
}

// 删除Payload
const removeItem4Payload = (pid: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmPayload(pid)
    return
  }
  console.error(`Unsupported remove path: ${pid}`)
}

// 添加Result
const addItem2Result = (
  content: Omit<VFNodeContentData, 'Hid' | 'Did'>,
  rid?: string,
  pos?: InsertPos,
) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addResult(content, rid, pos)
    return
  }
  console.error(`addItem2Result error`)
}

// 删除Result
const removeItem4Result = (rid: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmResult(rid)
    return
  }
  console.error(`Unsupported remove path: ${rid}`)
}

// Results添加项进Connect
const addResults2Connect = (
  handleid: string,
  result: any,
  rid: string | null = null,
  did: string | null = null,
  pos?: InsertPos,
) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addResultWithConnection(result, handleid, rid, did, pos)
    return
  }
  console.error('Unsupported append path')
}
// 从Connect删除Results
const removeResults4Connect = (rid: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmResultWithConnection(rid)
    return
  }
  console.error('Unsupported remove path')
}

// 添加Handle
const addHandle = (
  handleType: VFNodeConnectionType,
  handleId: string,
  handleLabel?: string,
  pos?: InsertPos,
) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addHandle(handleType, handleId, handleLabel, pos)
    if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
    return
  }
  console.error('Unsupported add handle')
}
// 删除Handle
const removeHandle = (handleType: VFNodeConnectionType, handleId: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmHandle(handleType, handleId)
    if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
    return
  }
  console.error('Unsupported remove handle')
}
// 添加Handle数据
const addHandleData = (
  handleType: VFNodeConnectionType,
  handleId: string,
  data: VFNodeHandleData,
  dataId?: string,
) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addHandleData(handleType, handleId, data, dataId)
    return
  }
  console.error('Unsupported add handle data')
}

// 删除Handle数据
const removeHandleData = (handleType: VFNodeConnectionType, handleId: string, dataId: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
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

// 这里需要递归解析result，解包ReadOnlyPropVar
const parseResult = (result: any, getValueFunc: Function) => {
  const parseValue = (value: any): any => {
    if (typeof value === 'object' && value !== null) {
      // 使用 zod 进行类型验证
      const ReadOnlyPropVarSchema = z
        .object({
          Type: z.enum([PropVarType.Value, PropVarType.VBind]),
          Data: z.any(),
          Replace: z.string().nullable().optional(),
        })
        .strict()
      if (ReadOnlyPropVarSchema.safeParse(value).success) {
        // This is a ReadOnlyPropVar
        return getValueFunc(value as ReadOnlyPropVar)
      } else if (Array.isArray(value)) {
        return value.map(parseValue)
      } else {
        const parsed: Record<string, any> = {}
        for (const [key, val] of Object.entries(value)) {
          parsed[key] = parseValue(val)
        }
        return parsed
      }
    }
    return value
  }

  return parseValue(result)
}

const replaceVBindProp = (prop: VBindProp): any => {
  if (prop.Replace) {
    const data = getValueByPath(prop)
    if (typeof data === 'string') {
      return prop.Replace.replace(/\{\{Data\}\}/g, (match, key) => {
        return data
      })
    }
  }
  return getValueByPath(prop)
}
const getPropValueFromReadOnlyPropVar = (prop: ReadOnlyPropVar): any => {
  switch (prop.Type) {
    case PropVarType.Value:
      return prop.Data
    case PropVarType.VBind:
      return replaceVBindProp(prop)
    default:
      return null
  }
}

// 属性处理器
const processedProps = computed(() => {
  const propsObj: Record<string, any> = {
    disabled: !isEditorMode.value,
  }
  const eventsObj: Record<string, Function> = {}

  for (const [propName, propVar] of Object.entries(
    (props.componentData as NormalComponent).Props || {},
  )) {
    const prop = propVar as PropVar
    switch (prop.Type) {
      case PropVarType.Value:
        propsObj[propName] = prop.Data
        break
      case PropVarType.VBind:
        propsObj[propName] = replaceVBindProp(prop)
        break
      case PropVarType.VModel:
        propsObj[propName] = getValueByPath(prop)
        eventsObj[`onUpdate:${propName}`] = (val: any) => {
          updateValueByPath(prop, val)
        }
        break
      case PropVarType.Function:
        const prop_Functions = prop as FunctionProp
        const functions: ((
          getFunc: (propvar: ReadOnlyPropVar | null | undefined) => any,
          setFunc: (key: string, value: any) => void,
        ) => void)[] = []

        for (const prop_Function of prop_Functions.Funcs) {
          if (prop_Function.Func == FunctionPropType.SETCONTEXT) {
            functions.push((_, setFunc) => {
              const { Key, Value } = prop_Function.Arg
              setFunc(getPropValueFromReadOnlyPropVar(Key), getPropValueFromReadOnlyPropVar(Value))
            })
          } else if (prop_Function.Func == FunctionPropType.ADDITEM) {
            const { ItemKey, ItemValue, DstPath } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addItemByPath(
                resolveDataPath(DstPath),
                getFunc(ItemKey),
                cloneDeep(parseResult(ItemValue, getFunc)),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEITEM) {
            const { ItemKey, DstPath } = prop_Function.Arg
            functions.push((getFunc, _) =>
              removeItemByPath(resolveDataPath(DstPath), getFunc(ItemKey)),
            )
          } else if (prop_Function.Func == FunctionPropType.APPENDITEM) {
            const { DstPath, ItemValue } = prop_Function.Arg
            functions.push((getFunc, _) =>
              appendItemByPath(
                resolveDataPath(DstPath),
                cloneDeep(parseResult(ItemValue, getFunc)),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDPAYLOAD) {
            const { Payload, PayloadId, Position } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addItem2Payload(
                cloneDeep(parseResult(Payload, getFunc)),
                getFunc(PayloadId),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEPAYLOAD) {
            const { PayloadId } = prop_Function.Arg
            functions.push((getFunc, _) => removeItem4Payload(getFunc(PayloadId)))
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT) {
            const { Result, ResultId, Position } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addItem2Result(cloneDeep(parseResult(Result, getFunc)), getFunc(ResultId), Position),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVERESULT) {
            const { ResultId } = prop_Function.Arg
            functions.push((getFunc, _) => removeItem4Result(getFunc(ResultId)))
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT2OUT) {
            const { HandleId, Result, ResultId, Position, DataId } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addResults2Connect(
                getFunc(HandleId),
                cloneDeep(parseResult(Result, getFunc)),
                getFunc(ResultId),
                getFunc(DataId),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVERESULT4OUT) {
            const { ResultId } = prop_Function.Arg
            functions.push((getFunc, _) => removeResults4Connect(getFunc(ResultId)))
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLE) {
            const { HandleType, HandleId, Position, HandleLabel } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addHandle(HandleType, getFunc(HandleId), cloneDeep(getFunc(HandleLabel)), Position),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLE) {
            const { HandleType, HandleId } = prop_Function.Arg
            functions.push((getFunc, _) => removeHandle(HandleType, getFunc(HandleId)))
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLEDATA) {
            const { HandleType, HandleId, Data, DataId } = prop_Function.Arg
            functions.push((getFunc, _) =>
              addHandleData(HandleType, getFunc(HandleId), Data, getFunc(DataId)),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLEDATA) {
            const { HandleType, HandleId, DataId } = prop_Function.Arg
            functions.push((getFunc, _) =>
              removeHandleData(HandleType, getFunc(HandleId), getFunc(DataId)),
            )
          } else if (prop_Function.Func == FunctionPropType.OPENEDITOR) {
            const { DstPath, Language } = prop_Function.Arg
            functions.push((__, _) => openCodeEditor(resolveDataPath(DstPath), Language))
          } else if (prop_Function.Func == FunctionPropType.UPDATENODEINTERNAL) {
            functions.push((__, _) => {
              if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
            })
          }
        }
        propsObj[propName] = () => {
          const f_Context: Record<string, any> = {}
          const getValueFrom_f_Context = (propvar: ReadOnlyPropVar | null | undefined) => {
            if (!propvar) return null
            if (propvar.Type === PropVarType.Value) {
              return propvar.Data
            } else if (propvar.Type === PropVarType.VBind) {
              const tmpfunc = {
                [CONTEXT_ARG]: (path: (string | number)[]) =>
                  path.reduce((acc, key) => acc?.[key], f_Context),
              }
              const data = getValueByPath(propvar, tmpfunc)
              if (propvar.Replace && typeof data === 'string') {
                return propvar.Replace.replace(/\{\{Data\}\}/g, (match, key) => {
                  return data
                })
              }
              return data
            }
          }
          const set_f_Context = (key: string, value: any) => {
            f_Context[key] = value
          }
          for (const func of functions) {
            func(getValueFrom_f_Context, set_f_Context)
          }
        }
        break
    }
  }

  return { ...propsObj, ...eventsObj }
})

// 条件判断系统
const resolveCondition = (condition?: Condition): boolean => {
  if (!condition) return true

  switch (condition.Type) {
    case TYPE_CONDITION_DIRECT:
      return getPropValueFromReadOnlyPropVar(condition.Condition)
    case TYPE_CONDITION_COMPARE:
      return handleCompare(condition)
    case TYPE_CONDITION_LOGICAL:
      return handleLogical(condition)
    default:
      return false
  }
}

const handleCompare = (config: CompareCondition): boolean => {
  const left = getPropValueFromReadOnlyPropVar(config.Left)
  const right = getPropValueFromReadOnlyPropVar(config.Right)

  const operators: Record<string, (a: any, b: any) => boolean> = {
    '==': (a, b) => a == b,
    '!=': (a, b) => a != b,
    '>': (a, b) => a > b,
    '<': (a, b) => a < b,
    '>=': (a, b) => a >= b,
    '<=': (a, b) => a <= b,
  }

  return operators[config.Operator]?.(left, right) ?? false
}

const handleLogical = (config: LogicalCondition) => {
  const results = config.Conditions.map(resolveCondition)
  return config.Operator === 'AND' ? results.every(Boolean) : results.some(Boolean)
}

// 获取Span组件的值
const getSpanValue = (config: SpanComponent): any => {
  if (config.Data.Type === PropVarType.VBind) {
    return replaceVBindProp(config.Data)
  } else if (config.Data.Type === PropVarType.Value) {
    return config.Data.Data
  } else {
    return null
  }
}

// 循环处理器
const handleForLoop = (config: ForLoopComponent) => {
  if (config.Type !== TYPE_VFOR) return null

  let items = []
  if (config.Items.Type === PropVarType.Value) {
    items = config.Items.Data
  } else if (config.Items.Type === PropVarType.VBind) {
    items = replaceVBindProp(config.Items)
  }
  const itemLabel = config.ItemLabel || '@Item'
  const indexLabel = config.IndexLabel || '@Index'

  if (typeof items !== 'object' || items === null) return null

  // 统一处理为键值数组格式
  const entries = Array.isArray(items)
    ? items.map((item, index) => [index, item])
    : Object.entries(items)

  const nodes = entries.map(([key, item]) => {
    const loopContext = {
      ...props.dataContext,
      [VFOR_DATA]: {
        ...props.dataContext[VFOR_DATA],
        [itemLabel]: item,
        [indexLabel]: key,
      },
    }

    if (Array.isArray(config.Template)) {
      return config.Template.map((template, index) => {
        return h(resolveComponent('DynamicComponent'), {
          key: `${indexLabel}-${key}-${index}`,
          componentData: template,
          dataContext: loopContext,
        })
      })
    } else {
      return h(resolveComponent('DynamicComponent'), {
        key: `${indexLabel}-${key}`,
        componentData: config.Template,
        dataContext: loopContext,
      })
    }
  })

  return h(Fragment, {}, nodes)
}

// 插槽处理器 - 直接返回插槽内容，不再包装为渲染函数
const processedSlots = computed(() => {
  return Object.entries((props.componentData as NormalComponent).Slots || {}).reduce(
    (acc, [name, content]) => {
      acc[name] = content
      return acc
    },
    {} as Record<string, BaseComponent | BaseComponent[]>,
  )
})

const resolveNormalComponent = (componentType: string) => {
  if (componentType === 'DynamicComponent') {
    return resolveComponent('DynamicComponent')
  } else if (DYNAMIC_COMPONENTS_MAP.hasOwnProperty(componentType)) {
    return DYNAMIC_COMPONENTS_MAP[componentType]
  } else if (DYNAMIC_FA_COMPONENTS_MAP.hasOwnProperty(componentType)) {
    return DYNAMIC_FA_COMPONENTS_MAP[componentType]
  } else if (DYNAMIC_ICONS_MAP.hasOwnProperty(componentType)) {
    return DYNAMIC_ICONS_MAP[componentType]
  } else {
    console.error(`Unsupported component type: ${componentType}`)
    return null
  }
}
</script>

<template>
  <!-- 先检查条件是否满足 -->
  <template v-if="resolveCondition(componentData.IfCondition)">
    <!-- 处理@FOR@类型组件 -->
    <component
      v-if="componentData.Type === TYPE_VFOR"
      :is="handleForLoop(componentData as ForLoopComponent)"
    />

    <!-- 处理@Value@或@VBind@类型组件 -->
    <span v-else-if="componentData.Type === TYPE_VSPAN">
      {{ getSpanValue(componentData as SpanComponent) }}
    </span>

    <!-- 处理普通组件 -->
    <component v-else :is="resolveNormalComponent(componentData.Type)" v-bind="processedProps">
      <!-- 递归渲染每个插槽 -->
      <template v-for="(slotContent, name) in processedSlots" #[name]="slotProps">
        <!-- 处理数组类型插槽内容 -->
        <template v-if="Array.isArray(slotContent)">
          <DynamicComponent
            v-for="(item, idx) in slotContent"
            :key="`slot-${name}-${idx}`"
            :component-data="item"
            :data-context="dataContext"
          />
        </template>

        <!-- 处理单个组件类型插槽内容 -->
        <DynamicComponent v-else :component-data="slotContent" :data-context="dataContext" />
      </template>
    </component>
  </template>
</template>
