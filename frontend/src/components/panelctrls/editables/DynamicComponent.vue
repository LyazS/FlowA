<script setup lang="ts">
import { h, resolveComponent, computed, Fragment, type VNode, type PropType } from 'vue'
import type {
  BaseComponent,
  NormalComponent,
  ForLoopComponent,
  SpanComponent,
  CompareCondition,
  LogicalCondition,
  PropVar,
  ReadOnlyPropVar,
  Condition,
} from '@/schemas/plugin_schemas'
import {
  PropVarType,
  THIS_NODE_DATA,
  VFOR_DATA,
  SELF_OPTIONS,
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
  otherContext: {
    type: Object as PropType<Record<string, any>>,
    default: () => ({}),
  },
})

// 数据路径解析依赖数组第一个元素来决定使用dataContext还是otherContext
// 数据路径解析器
const resolveValueByPath = (path: (string | number)[]): any => {
  const resolvePath: (string | number)[] = []
  for (const element of path) {
    if (
      resolvePath[0] === THIS_NODE_DATA &&
      props.dataContext.hasOwnProperty(element) &&
      typeof props.dataContext[element] === 'function'
    ) {
      resolvePath.push(...props.dataContext[element]())
    } else {
      resolvePath.push(element)
    }
  }
  if (resolvePath[0] === THIS_NODE_DATA) {
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.dataContext)
  } else if (resolvePath[0] === VFOR_DATA) {
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.otherContext[VFOR_DATA])
  } else if (resolvePath[0] === SELF_OPTIONS) {
    return resolvePath.slice(1).reduce((acc, key) => acc?.[key], props.otherContext[SELF_OPTIONS])
  }
}

// 数据更新器
const updateValueByPath = (path: (string | number)[], value: any) => {
  const resolvePath: (string | number)[] = []
  for (const element of path) {
    if (
      resolvePath[0] === THIS_NODE_DATA &&
      props.dataContext.hasOwnProperty(element) &&
      typeof props.dataContext[element] === 'function'
    ) {
      resolvePath.push(...props.dataContext[element]())
    } else {
      resolvePath.push(element)
    }
  }
  const firstKey = resolvePath.shift()!
  if (firstKey === THIS_NODE_DATA) {
    const lastKey = resolvePath.pop()!
    const parent = resolvePath.reduce((acc, key) => acc?.[key], props.dataContext)
    if (parent) parent[lastKey] = value
  } else {
    console.error('Unsupported update path')
  }
}

// 属性处理器
const processedProps = computed(() => {
  const propsObj: Record<string, any> = {}
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
        propsObj[propName] = resolveValueByPath(prop.Data)
        break
      case PropVarType.VModel:
        propsObj[propName] = resolveValueByPath(prop.Data)
        eventsObj[`onUpdate:${propName}`] = (val: any) => {
          updateValueByPath(prop.Data, val)
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
    case PropVarType.Value:
      return !!condition.Data
    case PropVarType.VBind:
      return !!resolveValueByPath(condition.Data)
    case TYPE_CONDITION_COMPARE:
      return handleCompare(condition)
    case TYPE_CONDITION_LOGICAL:
      return handleLogical(condition)
    default:
      return false
  }
}

const handleCompare = (config: CompareCondition): boolean => {
  const getValue = (source: ReadOnlyPropVar) =>
    source.Type === PropVarType.VBind ? resolveValueByPath(source.Data) : source.Data

  const left = getValue(config.Left)
  const right = getValue(config.Right)

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
  return config.Type === PropVarType.VBind ? resolveValueByPath(config.Data) : config.Data
}

// 循环处理器
const handleForLoop = (config: ForLoopComponent) => {
  if (config.Type !== TYPE_VFOR) return null

  let items = []
  if (config.Items.Type === PropVarType.Value) {
    items = config.Items.Data
  } else if (config.Items.Type === PropVarType.VBind) {
    items = resolveValueByPath(config.Items.Data)
  }
  const itemKey = config.ItemLabel || '@Item'
  const indexKey = config.IndexLabel || '@Index'

  if (!Array.isArray(items)) return null

  const nodes = items.map((item, index) => {
    const loopContext = {
      ...props.dataContext,
      [indexKey]: () => [index],
    }

    const loop_otherContext = {
      ...props.otherContext,
      [VFOR_DATA]: {
        ...props.otherContext[VFOR_DATA],
        [itemKey]: item,
        [indexKey]: index,
      },
    }

    if (Array.isArray(config.Template)) {
      return config.Template.map((template) => {
        return h(resolveComponent('DynamicComponent'), {
          key: index,
          componentData: template,
          dataContext: loopContext,
          otherContext: loop_otherContext,
        })
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
    <component v-else :is="resolveComponent(componentData.Type)" v-bind="processedProps">
      <!-- 递归渲染每个插槽 -->
      <template v-for="(slotContent, name) in processedSlots" #[name]="slotProps">
        <!-- 处理数组类型插槽内容 -->
        <template v-if="Array.isArray(slotContent)">
          <DynamicComponent
            v-for="(item, idx) in slotContent"
            :key="idx"
            :component-data="item"
            :data-context="dataContext"
            :other-context="otherContext"
          />
        </template>

        <!-- 处理单个组件类型插槽内容 -->
        <DynamicComponent
          v-else
          :component-data="slotContent"
          :data-context="dataContext"
          :other-context="otherContext"
        />
      </template>
    </component>
  </template>
</template>
