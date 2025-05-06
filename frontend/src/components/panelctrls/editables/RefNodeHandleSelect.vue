<template>
  <n-select
    :style="style"
    :value="computedValue"
    @update:value="updateValue"
    :options="computedOptions"
    :render-label="renderLabel"
    :disabled="!isEditorMode"
    :size="size"
    :placeholder="placeholder"
    :consistent-menu-width="false"
    placement="bottom-end"
  />
</template>

<script setup lang="ts">
import { h, type CSSProperties, computed } from 'vue'
import { NSelect, NText } from 'naive-ui'
import type { SelectOption } from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import { isEditorMode } from '@/hooks/useVFlowAttribute'
import isString from 'lodash/isString';
import { type RefNodeHandleItem } from '@/hooks/useNodeUtils'
import { VFNodeConnectionType } from '@/components/nodes/VFNodeInterface'
import type { NodeWithVFData } from '@/schemas/schemas'

const { findNode } = useVueFlow()
const props = withDefaults(
  defineProps<{
    value: RefNodeHandleItem | string | undefined | null
    options: RefNodeHandleItem[]
    size?: 'tiny' | 'small' | 'medium' | 'large'
    style?: CSSProperties
    placeholder?: string
  }>(),
  {
    size: 'small',
    style: () => ({}),
    placeholder: '请选择',
  },
)

const emit = defineEmits<{
  'update:value': [value: RefNodeHandleItem | string | undefined | null]
}>()

// 将 RefNodeHandleItem 转换为字符串 ID
const refNodeHandleItemToString = (item: RefNodeHandleItem): string => {
  return `${item.Node}:${item.HandleType}:${item.Handle}`
}

// 将字符串 ID 转换回 RefNodeHandleItem
const stringToRefNodeHandleItem = (str: string): RefNodeHandleItem | null => {
  const parts = str.split(':')
  if (parts.length === 3) {
    // 确保 HandleType 是有效的 VFNodeConnectionType
    const handleType = parts[1] as VFNodeConnectionType
    if (!(handleType in VFNodeConnectionType)) {
      return null
    }

    return {
      Node: parts[0],
      HandleType: handleType,
      Handle: parts[2],
    }
  }
  return null
}

// 检查值是否为 RefNodeHandleItem 类型
const isRefNodeHandleItem = (value: any): value is RefNodeHandleItem => {
  return (
    value &&
    typeof value === 'object' &&
    'Node' in value &&
    'HandleType' in value &&
    'Handle' in value
  )
}

// 计算属性：将 RefNodeHandleItem 转换为 n-select 需要的字符串值
const computedValue = computed({
  get: () => {
    if (!props.value) return null

    // 如果已经是字符串，直接返回
    if (typeof props.value === 'string') {
      return props.value
    }

    // 如果是 RefNodeHandleItem，转换为字符串
    if (isRefNodeHandleItem(props.value)) {
      return refNodeHandleItemToString(props.value)
    }

    return null
  },
  set: (val) => {
    updateValue(val)
  },
})

// 计算属性：将 RefNodeHandleItem 数组转换为 n-select 需要的选项格式
const computedOptions = computed(() => {
  return props.options.map((refItem) => {
    const itemstr = refNodeHandleItemToString(refItem)
    return {
      label: itemstr,
      value: itemstr,
    }
  })
})

// 更新值的方法
const updateValue = (value: string | null): void => {
  if (value === null || value === undefined) {
    emit('update:value', null)
    return
  }

  // 尝试将字符串转换为 RefNodeHandleItem
  const refItem = stringToRefNodeHandleItem(value)

  // 如果能成功转换为 RefNodeHandleItem，则发送 RefNodeHandleItem
  if (refItem) {
    emit('update:value', refItem)
  } else {
    // 如果不能转换，则直接发送字符串
    emit('update:value', value)
  }
}

const renderLabel = (option: SelectOption) => {
  try {
    if (!isString(option.label)) {
      throw new TypeError('label must be a string')
    }

    // 检查选项是否存在于计算后的选项列表中
    const isError = !computedOptions.value.some((select) => select.value === option.value)
    if (isError) {
      throw new Error('value not in options')
    }

    // 如果标签不是 RefNodeHandleItem 格式（不包含两个冒号），直接显示标签
    if (!option.label.includes(':') || option.label.split(':').length !== 3) {
      throw new Error('Invalid label format')
    }

    const [nodeId, handleType, handleId] = option.label.split(':')
    const node = findNode(nodeId) as NodeWithVFData

    // 如果找不到节点，直接显示原始标签
    if (!node) {
      throw new Error(`Cannot find node with id: ${nodeId}`)
    }

    const nLabel = node?.data.Label

    // 确保 handleType 是有效的 VFNodeConnectionType
    if (!(handleType in VFNodeConnectionType)) {
      throw new Error(`Invalid handleType: ${handleType}`)
    }

    // 安全地访问句柄数据
    const handleData = node?.data.Connections[handleType as VFNodeConnectionType]?.ById?.[handleId]
    if (!handleData) {
      throw new Error(`Cannot find handle data for ${handleType}:${handleId}`)
    }

    const hLabel = handleData.Label

    return [
      h(NText, { type: 'default', strong: true }, { default: () => `${nLabel}` }),
      h(NText, { type: 'default' }, { default: () => ' - ' }),
      h(NText, { type: 'info' }, { default: () => hLabel }),
    ]
  } catch (e) {
    return h(NText, { type: 'error', strong: true }, { default: () => `❌${option.label}` })
  }
}
</script>
