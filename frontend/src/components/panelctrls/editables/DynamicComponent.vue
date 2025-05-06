<script setup lang="ts">
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
  VARetFuncPropSchema,
} from '@/schemas/plugin_schemas'
import {
  DYNAMIC_COMPONENTS_MAP,
  DYNAMIC_FA_COMPONENTS_MAP,
  DYNAMIC_ICONS_MAP,
  EXTRA_DIV_COMPONENTS,
} from '@/schemas/dynamic_components_map'
import {
  selectedNodeId,
  isEditorMode,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { cloneDeep } from 'lodash'
import { useDynamicComp } from '@/hooks/useDynamicComp'
import { lodashOperators } from '@/utils/tools'

defineOptions({
  name: 'DynamicComponent',
})
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
const { updateNodeInternals } = useVueFlow()
const {
  resolveDataPath,
  getValueByPath,
  updateValueByPath,
  setItemByPath,
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
  deleteImage,
  getValueFromROP,
  getValueFromROPAsync,
} = useDynamicComp()

// 这里需要递归解析result，解包ReadOnlyPropVar
const parseResult = async (result: any, getValueFunc: Function) => {
  const parseValue = async (value: any): Promise<any> => {
    if (typeof value === 'object' && value !== null) {
      // 使用 zod 进行类型验证
      if (ValuePropSchema.safeParse(value).success || VBindPropSchema.safeParse(value).success) {
        // This is a ReadOnlyPropVar
        return await getValueFunc(value as ReadOnlyPropVar)
      } else if (
        VRetFuncPropSchema.safeParse(value).success ||
        VARetFuncPropSchema.safeParse(value).success
      ) {
        return await getValueFromROPAsync(props.dataContext, value)
      } else if (Array.isArray(value)) {
        return await Promise.all(value.map(parseValue))
      } else {
        const parsed: Record<string, any> = {}
        for (const [key, val] of Object.entries(value)) {
          parsed[key] = await parseValue(val)
        }
        return parsed
      }
    }
    return value
  }

  return await parseValue(result)
}

// 属性处理器
const processedProps = computed(() => {
  const propsObj: Record<string, any> = {
    disabled: !isEditorMode.value,
  }

  const processValuePropRecursively = (parent: any, key: string, value: any) => {
    if (value === null || value === undefined) {
      parent[key] = value
    } else if (Array.isArray(value)) {
      // 处理数组，递归处理每个元素
      const processedArray: any[] = []
      for (let i = 0; i < value.length; i++) {
        const tempObj: Record<string, any> = {}
        processValuePropRecursively(tempObj, 'item', value[i])
        processedArray.push(tempObj.item)
      }
      parent[key] = processedArray
    } else if (typeof value === 'object') {
      if (ValuePropSchema.safeParse(value).success) {
        // This is a ValueProp
        processValuePropRecursively(parent, key, value.FA_Data__)
      } else if (VBindPropSchema.safeParse(value).success) {
        // This is a VBindProp
        parent[key] = getValueByPath(props.dataContext, value)
      } else if (VModelPropSchema.safeParse(value).success) {
        // This is a VModelProp
        parent[key] = getValueByPath(props.dataContext, value)
        parent[`onUpdate:${key}`] = (val: any) => {
          updateValueByPath(props.dataContext, value, val)
        }
      } else if (VOpFuncPropSchema.safeParse(value).success) {
        // This is a FunctionProp
        const prop_Functions = value as OperateFunctionProp
        const functions: ((
          getFunc: (propvar: ReadOnlyPropVar | null | undefined) => Promise<any>,
          setFunc: (key: string, value: any) => void,
        ) => Promise<void>)[] = []

        for (const prop_Function of prop_Functions.FA_Funcs__) {
          if (prop_Function.Func == FunctionPropType.SETCONTEXT) {
            functions.push(async (_, setFunc) => {
              const { Key, Value } = prop_Function.Arg
              setFunc(
                await getValueFromROPAsync(props.dataContext, Key),
                await getValueFromROPAsync(props.dataContext, Value),
              )
            })
          } else if (prop_Function.Func == FunctionPropType.SETITEM) {
            const { DstPath, ItemValue } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              setItemByPath(
                props.dataContext,
                resolveDataPath(props.dataContext, DstPath),
                cloneDeep(await parseResult(ItemValue, getFunc)),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDITEM) {
            const { ItemKey, ItemValue, DstPath } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addItemByPath(
                props.dataContext,
                resolveDataPath(props.dataContext, DstPath),
                await getFunc(ItemKey),
                cloneDeep(await parseResult(ItemValue, getFunc)),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEITEM) {
            const { ItemKey, DstPath } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeItemByPath(
                props.dataContext,
                resolveDataPath(props.dataContext, DstPath),
                await getFunc(ItemKey),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.APPENDITEM) {
            const { DstPath, ItemValue, Position } = prop_Function.Arg
            functions.push(async (getFunc, _) => {
              appendItemByPath(
                props.dataContext,
                resolveDataPath(props.dataContext, DstPath),
                cloneDeep(await parseResult(ItemValue, getFunc)),
                Position,
              )
            })
          } else if (prop_Function.Func == FunctionPropType.ADDPAYLOAD) {
            const { Payload, PayloadId, Position } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addItem2Payload(
                props.dataContext,
                cloneDeep(await parseResult(Payload, getFunc)),
                await getFunc(PayloadId),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEPAYLOAD) {
            const { PayloadId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeItem4Payload(props.dataContext, await getFunc(PayloadId)),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT) {
            const { Result, ResultId, Position } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addItem2Result(
                props.dataContext,
                cloneDeep(await parseResult(Result, getFunc)),
                await getFunc(ResultId),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVERESULT) {
            const { ResultId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeItem4Result(props.dataContext, await getFunc(ResultId)),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDRESULT2OUT) {
            const { HandleId, Result, ResultId, Position, DataId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addResults2Connect(
                props.dataContext,
                await getFunc(HandleId),
                cloneDeep(await parseResult(Result, getFunc)),
                await getFunc(ResultId),
                await getFunc(DataId),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVERESULT4OUT) {
            const { ResultId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeResults4Connect(props.dataContext, await getFunc(ResultId)),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLE) {
            const { HandleType, HandleId, Position, HandleLabel } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addHandle(
                props.dataContext,
                HandleType,
                await getFunc(HandleId),
                cloneDeep(await getFunc(HandleLabel)),
                Position,
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLE) {
            const { HandleType, HandleId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeHandle(props.dataContext, HandleType, await getFunc(HandleId)),
            )
          } else if (prop_Function.Func == FunctionPropType.ADDHANDLEDATA) {
            const { HandleType, HandleId, Data, DataId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              addHandleData(
                props.dataContext,
                HandleType,
                await getFunc(HandleId),
                Data,
                await getFunc(DataId),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.REMOVEHANDLEDATA) {
            const { HandleType, HandleId, DataId } = prop_Function.Arg
            functions.push(async (getFunc, _) =>
              removeHandleData(
                props.dataContext,
                HandleType,
                await getFunc(HandleId),
                await getFunc(DataId),
              ),
            )
          } else if (prop_Function.Func == FunctionPropType.OPENEDITOR) {
            const { DstPath, Language } = prop_Function.Arg
            functions.push(async (__, _) =>
              openCodeEditor(resolveDataPath(props.dataContext, DstPath), Language),
            )
          } else if (prop_Function.Func == FunctionPropType.UPDATENODEINTERNAL) {
            functions.push(async (__, _) => {
              if (selectedNodeId.value) updateNodeInternals([selectedNodeId.value])
            })
          } else if (prop_Function.Func == FunctionPropType.DELETEIMAGE) {
            const { Filename } = prop_Function.Arg
            functions.push(async (getFunc, _) => {
              const filename = await getFunc(Filename)
              if (filename) {
                await deleteImage(filename)
              }
            })
          }
        }
        parent[key] = async () => {
          const f_Context: Record<string, any> = {}
          const getValueFrom_f_Context = async (propvar: ReadOnlyPropVar | null | undefined) => {
            if (!propvar) return null
            if (propvar.FA_Type__ === PropVarType.Value) {
              return propvar.FA_Data__
            } else if (propvar.FA_Type__ === PropVarType.VBind) {
              const tmpfunc = {
                [ARG_CONTEXT]: (path: (string | number)[]) =>
                  path.reduce((acc, key) => acc?.[key], f_Context),
              }
              const data = await getValueFromROPAsync(props.dataContext, propvar, tmpfunc)
              return data
            }
          }
          const set_f_Context = (key: string, value: any) => {
            f_Context[key] = value
          }
          // 执行函数，检查返回值是否为Promise
          for (const func of functions) {
            await func(getValueFrom_f_Context, set_f_Context)
          }
        }
      } else if (VRetFuncPropSchema.safeParse(value).success) {
        parent[key] = getValueFromROP(props.dataContext, value)
      } else {
        // This is a plain object, process each property recursively
        const processedObj: Record<string, any> = {}
        for (const [objKey, objValue] of Object.entries(value)) {
          processValuePropRecursively(processedObj, objKey, objValue)
        }
        parent[key] = processedObj
      }
    } else {
      // This is a primitive value, just assign it
      parent[key] = value
    }
  }

  for (const [propName, propVar] of Object.entries(
    (props.componentData as NormalComponent).Props || {},
  )) {
    processValuePropRecursively(propsObj, propName, propVar)
  }

  return propsObj
})

// 条件判断系统
const resolveCondition = (condition?: Condition): boolean => {
  if (!condition) return true

  switch (condition.Type) {
    case TYPE_CONDITION_DIRECT:
      return getValueFromROP(props.dataContext, condition.Condition)
    case TYPE_CONDITION_COMPARE:
      return handleCompare(condition)
    case TYPE_CONDITION_LOGICAL:
      return handleLogical(condition)
    default:
      return false
  }
}

const handleCompare = (config: CompareCondition): boolean => {
  const left = getValueFromROP(props.dataContext, config.Left)
  const right = getValueFromROP(props.dataContext, config.Right)

  return lodashOperators[config.Operator]?.(left, right) ?? false
}

const handleLogical = (config: LogicalCondition) => {
  const results = config.Conditions.map(resolveCondition)
  return config.Operator === 'AND' ? results.every(Boolean) : results.some(Boolean)
}

// 获取Span组件的值
const getSpanValue = (config: SpanComponent): any => {
  if (config.Data.FA_Type__ === PropVarType.VBind) {
    return getValueByPath(props.dataContext, config.Data)
  } else if (config.Data.FA_Type__ === PropVarType.Value) {
    return config.Data.FA_Data__
  } else {
    return null
  }
}

// 循环处理器
const handleForLoop = (config: ForLoopComponent) => {
  if (config.Type !== TYPE_VFOR) return null

  let items = []
  if (config.Items.FA_Type__ === PropVarType.Value) {
    items = config.Items.FA_Data__
  } else if (config.Items.FA_Type__ === PropVarType.VBind) {
    items = getValueByPath(props.dataContext, config.Items)
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
  } else if (
    [
      'div',
      'span',
      'p',
      'h1',
      'h2',
      'h3',
      'h4',
      'h5',
      'h6',
      'ul',
      'ol',
      'li',
      'a',
      'img',
      'button',
      'input',
      'textarea',
      'select',
      'option',
    ].includes(componentType.toLowerCase())
  ) {
    // 处理原生HTML元素
    return componentType.toLowerCase()
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
      <template v-for="(slotContent, name) in processedSlots" #[name]>
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
        <template v-else>
          <div v-if="EXTRA_DIV_COMPONENTS.includes(componentData.Type)">
            <DynamicComponent :component-data="slotContent" :data-context="dataContext" />
          </div>
          <DynamicComponent v-else :component-data="slotContent" :data-context="dataContext" />
        </template>
      </template>
    </component>
  </template>
</template>
