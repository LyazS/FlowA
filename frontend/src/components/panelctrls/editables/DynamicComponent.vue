<script setup lang="ts">
import {
  h,
  defineOptions,
  resolveComponent,
  computed,
  Fragment,
  type VNode,
  type PropType,
} from 'vue'
import type {
  PropVarBase,
  ValueProp,
  VBindProp,
  VModelProp,
  VForProps,
  BaseComponent,
  CompareCondition,
  LogicalCondition,
  ValueCondition,
  VBindCondition,
  ComponentProp,
  Condition,
} from '@/schemas/plugin_schemas'
import { PropVarType } from '@/schemas/plugin_schemas'

defineOptions({
  name: 'DynamicComponent', // 必须定义组件名
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

const resolveValueByPath = (path: (string | number)[]): any => {
  let current: any = props.dataContext
  for (const key of path) {
    current = current?.[key]
    if (current === undefined) break
  }
  return current
}

const updateValueByPath = (path: (string | number)[], value: any) => {
  const pathCopy = [...path]
  const lastKey = pathCopy.pop()!
  let context: any = props.dataContext
  for (const key of pathCopy) {
    if (!context[key]) context[key] = {}
    context = context[key]
  }
  context[lastKey] = value
}

const processedProps = computed(() => {
  const propsObj: Record<string, any> = {}
  const eventsObj: Record<string, (value: any) => void> = {}

  for (const [propName, propVar] of Object.entries(props.componentData.Props || {})) {
    const prop = propVar as ComponentProp
    switch (prop.Type) {
      case PropVarType.Value:
        propsObj[propName] = prop.Data
        break
      case PropVarType.VBind:
        propsObj[propName] = computed(() => resolveValueByPath(prop.Data))
        break
      case PropVarType.VModel: {
        const modelValue = computed({
          get: () => resolveValueByPath(prop.Data),
          set: (value) => updateValueByPath(prop.Data, value),
        })
        propsObj[propName] = modelValue.value
        eventsObj[`onUpdate:${propName}`] = (value: any) => {
          modelValue.value = value
        }
        break
      }
    }
  }

  return { ...propsObj, ...eventsObj }
})

const resolveCondition = (config?: Condition): any => {
  if (!config) return true

  switch (config.Type) {
    case PropVarType.Value:
      return config.Data
    case PropVarType.VBind:
      return resolveValueByPath(config.Data)
    case 'Compare':
      return handleCompare(config)
    case 'Logical':
      return handleLogical(config)
    default:
      console.warn('未知的条件类型:', (config as any).Type)
      return false
  }
}

const handleCompare = (config: CompareCondition): boolean => {
  const left = resolveCondition(config.Left)
  const right = resolveCondition(config.Right)
  const operator = config.Operator

  const comparisons: Record<string, (a: any, b: any) => boolean> = {
    '==': (a, b) => a == b,
    '===': (a, b) => a === b,
    '!=': (a, b) => a != b,
    '!==': (a, b) => a !== b,
    '>': (a, b) => a > b,
    '<': (a, b) => a < b,
    '>=': (a, b) => a >= b,
    '<=': (a, b) => a <= b,
  }

  return comparisons[operator]?.(left, right) ?? false
}

const handleLogical = (config: LogicalCondition): boolean => {
  const conditions = config.Conditions.map(resolveCondition)

  return {
    AND: () => conditions.every(Boolean),
    OR: () => conditions.some(Boolean),
  }[config.Operator]?.()
}

const renderSlotContent = (
  content: BaseComponent | BaseComponent[] | undefined,
  depth = 0,
): VNode | VNode[] | null => {
  if (depth > 10) return null
  if (!content) return null

  if (Array.isArray(content)) {
    return h(
      Fragment,
      {},
      content.map((child) => renderSlotContent(child, depth + 1)),
    )
  }

  const slotContent = content as BaseComponent
  if (!slotContent.Type) return null

  if (slotContent.Type === '@DIRECT_CONTENT') {
    const prop = slotContent.Props?.value as ComponentProp
    switch (prop.Type) {
      case PropVarType.Value:
        return h('span', prop.Data)
      case PropVarType.VBind:
        return h('span', resolveValueByPath(prop.Data))
      default:
        return null
    }
  }

  if (slotContent.Type === '@VFor') {
    const vForProps = slotContent.Props as unknown as VForProps
    const itemsProp = vForProps.items
    let items: any[] = []

    if (itemsProp.Type === PropVarType.VBind) {
      items = resolveValueByPath(itemsProp.Data) || []
    } else if (itemsProp.Type === PropVarType.Value) {
      items = itemsProp.Data
    }

    return h(
      Fragment,
      {},
      items.map((item, index) => {
        const loopContext = {
          ...props.dataContext,
          [vForProps.itemLabel]: item,
          [vForProps.indexLabel]: index,
        }
        return h(resolveComponent('DynamicComponent'), {
          componentData: vForProps.template,
          dataContext: loopContext,
        })
      }),
    )
  }

  return h(resolveComponent('DynamicComponent'), {
    componentData: slotContent,
    dataContext: props.dataContext,
  })
}

const processedSlots = computed(() => {
  const slots: Record<string, (props: any) => VNode> = {}
  for (const [slotName, slotContent] of Object.entries(props.componentData.Slots || {})) {
    const content = renderSlotContent(slotContent)
    if (content) {
      slots[slotName] = (props: any) => {
        return h(Fragment, {}, [content])
      }
    }
  }
  return slots
})
</script>

<template>
  <component
    v-if="resolveCondition(componentData.IfCondition)"
    :is="resolveComponent(componentData.Type)"
    v-bind="processedProps"
  >
    <template v-for="(slotFunc, slotName) in processedSlots" #[slotName]="slotProps">
      <component :is="slotFunc(slotProps)" />
    </template>
  </component>
</template>
