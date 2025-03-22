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
  Condition,
} from '@/schemas/plugin_schemas'
import { PropVarType } from '@/schemas/plugin_schemas'

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

// 数据路径解析器
const resolveValueByPath = (path: (string | number)[]): any => {
  return path.reduce((acc, key) => acc?.[key], props.dataContext)
}

// 数据更新器
const updateValueByPath = (path: (string | number)[], value: any) => {
  const clonePath = [...path]
  const lastKey = clonePath.pop()!
  const parent = clonePath.reduce((acc, key) => acc?.[key], props.dataContext)
  if (parent) parent[lastKey] = value
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
    case 'Value':
      return !!condition.Data
    case 'VBind':
      return !!resolveValueByPath(condition.Data)
    case 'Compare':
      return handleCompare(condition)
    case 'Logical':
      return handleLogical(condition)
    default:
      return false
  }
}

const handleCompare = (config: CompareCondition): boolean => {
  const getValue = (source: PropVar) =>
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
  return config.Type === '@VBind@' ? resolveValueByPath(config.Data) : config.Data
}

// 循环处理器
const handleForLoop = (config: ForLoopComponent) => {
  if (config.Type !== '@FOR@') return null

  const itemPath = config.Items?.Data || []
  const items = resolveValueByPath(itemPath)
  const itemKey = config.ItemLabel || '@Item'
  const indexKey = config.IndexLabel || '@Index'

  if (!Array.isArray(items)) return null

  const nodes = items.map((item, index) => {
    const loopContext = {
      ...props.dataContext,
      [itemKey]: item,
      [indexKey]: index,
    }

    return h(resolveComponent('DynamicComponent'), {
      key: index,
      componentData: config.Template,
      dataContext: loopContext,
    })
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
      v-if="componentData.Type === '@FOR@'"
      :is="handleForLoop(componentData as ForLoopComponent)"
    />

    <!-- 处理@Value@或@VBind@类型组件 -->
    <span v-else-if="componentData.Type === '@Value@' || componentData.Type === '@VBind@'">
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
          />
        </template>

        <!-- 处理单个组件类型插槽内容 -->
        <DynamicComponent v-else :component-data="slotContent" :data-context="dataContext" />
      </template>
    </component>
  </template>
</template>
