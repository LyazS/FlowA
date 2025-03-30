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
} from 'vue'
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
  ValueProp,
} from '@/schemas/plugin_schemas'
import {
  PropVarType,
  FunctionPropType,
  THIS_NODE_DATA,
  CONTEXT_FUNCTION,
  VFOR_DATA,
  CONNECT_OPTIONS,
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
import { VFNode } from '@/components/nodes/VFNodeClass'
import {
  isEditorMode,
  isEditing,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { type SelectOption } from 'naive-ui'
import { type CodeEditorLanguage } from '@/components/nodes/VFNodeInterface'

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
const getOrCreateVarSelection =
  inject<(path: string[]) => ComputedRef<SelectOption[]>>('getOrCreateVarSelection')!

// 数据路径解析器
const resolveDataPath = (path: (string | number)[]): (string | number)[] => {
  // 解析路径
  const resolvePath: (string | number)[] = []
  for (const element of path) {
    if (
      resolvePath[0] === THIS_NODE_DATA &&
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
  } else if (resolvePath[0] === CONNECT_OPTIONS) {
    if (resolvePath.length === 3) {
      return getOrCreateVarSelection(resolvePath.slice(1) as string[])
    } else {
      console.error('Invalid connect option path')
      return null
    }
  }
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

// Results添加项
const addItem2Results = (handleid: string, result: any) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.addResultWithConnection(result, handleid)
    return
  }
  console.error('Unsupported append path')
}
// Results删除项
const removeItem4Results = (rid: string) => {
  const nodedata = props.dataContext[THIS_NODE_DATA] as VFNode
  if (nodedata) {
    nodedata.rmResultWithConnection(rid)
    return
  }
  console.error('Unsupported remove path')
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
const getPropValueFromReadOnlyPropVar = (prop: ReadOnlyPropVar): any => {
  switch (prop.Type) {
    case PropVarType.Value:
      return prop.Data
    case PropVarType.VBind:
      return getValueByPath(prop.Data)
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
        propsObj[propName] = getValueByPath(prop.Data)
        break
      case PropVarType.VModel:
        propsObj[propName] = getValueByPath(prop.Data)
        eventsObj[`onUpdate:${propName}`] = (val: any) => {
          updateValueByPath(prop.Data, val)
        }
        break
      case PropVarType.Function:
        const prop_Function = prop as FunctionProp
        if (prop_Function.Func == FunctionPropType.ADDITEM) {
          const { ItemKey, ItemValue, DstPath } = prop_Function.Arg
          if (!!ItemKey && !!ItemValue && !!DstPath) {
            propsObj[propName] = () =>
              addItemByPath(DstPath, getPropValueFromReadOnlyPropVar(ItemKey), ItemValue)
          } else {
            console.error('Invalid add item function')
          }
        } else if (prop_Function.Func == FunctionPropType.REMOVEITEM) {
          const { ItemKey, DstPath } = prop_Function.Arg
          if (!!ItemKey && !!DstPath) {
            propsObj[propName] = () =>
              removeItemByPath(DstPath, getPropValueFromReadOnlyPropVar(ItemKey))
          } else {
            console.error('Invalid remove item function')
          }
        } else if (prop_Function.Func == FunctionPropType.APPENDITEM) {
          const { DstPath, ItemValue } = prop_Function.Arg
          if (!!ItemValue && !!DstPath) {
            propsObj[propName] = () => appendItemByPath(DstPath, ItemValue)
          } else {
            console.error('Invalid append item function')
          }
        } else if (prop_Function.Func == FunctionPropType.ADDRESULT2OUT) {
          const { HandleId, Result } = prop_Function.Arg
          if (!!HandleId && !!Result) {
            propsObj[propName] = () => addItem2Results(HandleId, Result)
          } else {
            console.error('Invalid add result function')
          }
        } else if (prop_Function.Func == FunctionPropType.REMOVERESULT4OUT) {
          const { ResultId } = prop_Function.Arg
          if (!!ResultId) {
            propsObj[propName] = () => removeItem4Results(getPropValueFromReadOnlyPropVar(ResultId))
          } else {
            console.error('Invalid remove result function')
          }
        } else if (prop_Function.Func == FunctionPropType.OPENEDITOR) {
          const { DstPath, Language } = prop_Function.Arg
          if (!!DstPath && !!Language) {
            propsObj[propName] = () => openCodeEditor(DstPath, Language)
          } else {
            console.error('Invalid open code editor function')
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
  return config.Type === PropVarType.VBind ? getValueByPath(config.Data) : config.Data
}

// 循环处理器
const handleForLoop = (config: ForLoopComponent) => {
  if (config.Type !== TYPE_VFOR) return null

  let items = []
  if (config.Items.Type === PropVarType.Value) {
    items = config.Items.Data
  } else if (config.Items.Type === PropVarType.VBind) {
    items = getValueByPath(config.Items.Data)
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
