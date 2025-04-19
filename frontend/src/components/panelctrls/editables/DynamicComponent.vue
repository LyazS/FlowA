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
  TYPE_VALUE,
  TYPE_VBIND,
  TYPE_VMODEL,
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
import { useNodeUtils, type VarItem } from '@/hooks/useNodeUtils'
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
const { mapVarItemToSelect } = useNodeUtils()
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
const getOrCreateVarSelection = inject<(path: string[]) => VarItem[]>('getOrCreateVarSelection')!
const getOrCreateVarSelectionWHandle = inject<(path: string[]) => Record<string, VarItem[]>>(
  'getOrCreateVarSelectionWHandle',
)!
const getNodeConfig = inject<(nid: string) => any>('getNodeConfig')!

const getConnectionsByArgs = inject<
  (args: string[]) =>
    | string[] // 节点层级-节点数组
    | Record<string, Record<string, string[]>> // 句柄层级-句柄字典
    | VarItem[] // 变量层级-变量数组
    | SelectOption[] // 变量层级-变量选项/句柄层级-句柄选项
    | null
>('getConnectionsByArgs')!

// 数据路径解析器
const resolveDataPath = (path: (string | number)[]): (string | number)[] => {
  // 解析路径
  const resolvePath: (string | number)[] = []
  for (const element of path) {
    if (
      (resolvePath[0] === THIS_NODE_DATA || resolvePath[0] === CONNECT_DATA) &&
      props.dataContext[CONTEXT_FUNCTION].hasOwnProperty(element) &&
      typeof props.dataContext[CONTEXT_FUNCTION][element] === 'function'
    ) {
      resolvePath.push(...props.dataContext[CONTEXT_FUNCTION][element]())
    } else {
      resolvePath.push(element)
    }
  }
  return resolvePath
}

// 数据获取依赖数组第一个元素来决定使用字典
const getValueByPath = (path: (string | number)[]): any => {
  const resolvePath: (string | number)[] = resolveDataPath(path)
  // 根据路径取值
  if (resolvePath[0] === THIS_NODE_DATA) {
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
  } else if (resolvePath[0] === VFOR_DATA) {
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext[VFOR_DATA])
  } else if (resolvePath[0] === CONNECT_DATA_TO_SELECT) {
    if (resolvePath.length >= 2) {
      return getOrCreateVarSelection(resolvePath.slice(1) as string[]).map((item) =>
        mapVarItemToSelect(item),
      )
    }
  } else if (resolvePath[0] === CONNECT_DATA) {
    if (resolvePath.length >= 2) {
      const res = getConnectionsByArgs(resolvePath.slice(1) as string[])
      return res
    }
  } else if (resolvePath[0] === NODE_CONFIG_DATA) {
    const nodeConfig = getNodeConfig(selectedNodeId.value as string)
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], nodeConfig)
  } else if (resolvePath[0] === GENERATE_UUID) {
    return getUuid()
  }
  console.error('Invalid connect option path')
  return null
}

// 数据更新
const updateValueByPath = (path: (string | number)[], value: any) => {
  // 解析路径
  const resolvePath: (string | number)[] = resolveDataPath(path)
  // 根据路径更新值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const lastKey = resolvePath.pop()!
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) parent[lastKey] = value
  } else {
    console.error('Unsupported update path')
  }
}

// Object类型数据添加项
const addItemByPath = (path: (string | number)[], key: string | number, value: any) => {
  // 解析路径
  const resolvePath: (string | number)[] = resolveDataPath(path)
  // 根据路径添加值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) {
      parent[key] = value
      return
    }
  }
  console.error('Unsupported add path')
}
// Object|Array类型数据删除项
const removeItemByPath = (path: (string | number)[], key: string | number) => {
  // 解析路径
  const resolvePath: (string | number)[] = resolveDataPath(path)
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
  console.error('Unsupported delete path')
}

// Array类型数据添加项
const appendItemByPath = (path: (string | number)[], value: any) => {
  // 解析路径
  const resolvePath: (string | number)[] = resolveDataPath(path)
  // 根据路径插入值
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext[THIS_NODE_DATA])
    if (parent) {
      parent.push(value)
      return
    }
  }
  console.error('Unsupported append path')
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
  console.error('Unsupported append path')
}

// 删除Result
const removeItem4Result = (rid: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmResult(rid)
    return
  }
  console.error('Unsupported remove path')
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
const openCodeEditor = (path: (string | number)[], lang: CodeEditorLanguage) => {
  // 解析路径
  const resolvePath: (string | number)[] = resolveDataPath(path)
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
          Replace: z.string().optional(),
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

const replaceVBindProp = (prop: VBindProp | SpanComponent): any => {
  if (prop.Replace) {
    const data = getValueByPath(prop.Data)
    if (typeof data === 'string') {
      return prop.Replace.replace(/\{\{Data\}\}/g, (match, key) => {
        return data
      })
    }
  }
  return getValueByPath(prop.Data)
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
        propsObj[propName] = getValueByPath(prop.Data)
        eventsObj[`onUpdate:${propName}`] = (val: any) => {
          updateValueByPath(prop.Data, val)
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
            functions.push((getFunc, setFunc) => {
              const { Key, Value } = prop_Function.Arg
              setFunc(getPropValueFromReadOnlyPropVar(Key), getPropValueFromReadOnlyPropVar(Value))
            })
          } else if (prop_Function.Func == FunctionPropType.ADDITEM) {
            const { ItemKey, ItemValue, DstPath } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              addItemByPath(DstPath, getFunc(ItemKey), cloneDeep(parseResult(ItemValue, getFunc))),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEITEM) {
            const { ItemKey, DstPath } = prop_Function.Arg
            functions.push((getFunc, setFunc) => removeItemByPath(DstPath, getFunc(ItemKey)))
          } else if (prop_Function.Func == FunctionPropType.APPENDITEM) {
            const { DstPath, ItemValue } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              appendItemByPath(DstPath, cloneDeep(parseResult(ItemValue, getFunc))),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT) {
            const { Result, ResultId, Position } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              addItem2Result(cloneDeep(parseResult(Result, getFunc)), getFunc(ResultId), Position),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVERESULT) {
            const { ResultId } = prop_Function.Arg
            functions.push((getFunc, setFunc) => removeItem4Result(getFunc(ResultId)))
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT2OUT) {
            const { HandleId, Result, ResultId, Position, DataId } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
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
            functions.push((getFunc, setFunc) => removeResults4Connect(getFunc(ResultId)))
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLE) {
            const { HandleType, HandleId, Position, HandleLabel } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              addHandle(HandleType, getFunc(HandleId), cloneDeep(getFunc(HandleLabel)), Position),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLE) {
            const { HandleType, HandleId } = prop_Function.Arg
            functions.push((getFunc, setFunc) => removeHandle(HandleType, getFunc(HandleId)))
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLEDATA) {
            const { HandleType, HandleId, Data, DataId } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              addHandleData(HandleType, getFunc(HandleId), Data, getFunc(DataId)),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLEDATA) {
            const { HandleType, HandleId, DataId } = prop_Function.Arg
            functions.push((getFunc, setFunc) =>
              removeHandleData(HandleType, getFunc(HandleId), getFunc(DataId)),
            )
          } else if (prop_Function.Func == FunctionPropType.OPENEDITOR) {
            const { DstPath, Language } = prop_Function.Arg
            functions.push((getFunc, setFunc) => openCodeEditor(DstPath, Language))
          } else if (prop_Function.Func == FunctionPropType.UPDATENODEINTERNAL) {
            functions.push((getFunc, setFunc) => {
              if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
            })
          }
        }
        propsObj[propName] = () => {
          const f_Context: Record<string, any> = {}
          const getValueFrom_f_Context = (propvar: ReadOnlyPropVar | null | undefined) => {
            if (!propvar) return null
            if (propvar.Type === PropVarType.VBind && propvar.Data[0] === CONTEXT_ARG) {
              const data = propvar.Data.slice(1).reduce((acc, key) => acc?.[key], f_Context)
              if (propvar.Replace && typeof data === 'string') {
                return propvar.Replace.replace(/\{\{Data\}\}/g, (match, key) => {
                  return data
                })
              }
              return data
            }
            return getPropValueFromReadOnlyPropVar(propvar)
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
  return config.Type === PropVarType.VBind ? replaceVBindProp(config) : config.Data
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
      [CONTEXT_FUNCTION]: {
        ...props.dataContext[CONTEXT_FUNCTION],
        [itemLabel]: () => [item],
        [indexLabel]: () => [key],
      },
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
    <span v-else-if="componentData.Type === TYPE_VALUE || componentData.Type === TYPE_VBIND">
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
