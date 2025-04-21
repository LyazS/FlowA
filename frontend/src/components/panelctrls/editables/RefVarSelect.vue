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
import { isString } from '@/utils/tools'
import { type RefVarItem } from '@/hooks/useNodeUtils'
import type { NodeWithVFData } from '@/schemas/schemas'
const { findNode } = useVueFlow()
const props = withDefaults(
  defineProps<{
    value: RefVarItem | string | undefined | null
    options: RefVarItem[]
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
  'update:value': [value: RefVarItem | string | undefined | null]
}>()

// 将 RefVarItem 转换为字符串 ID
const refVarItemToString = (item: RefVarItem): string => {
  return `${item.Nid}:${item.Path.ContentName}:${item.Path.ContentId}`
}

// 将字符串 ID 转换回 RefVarItem
const stringToRefVarItem = (str: string): RefVarItem | null => {
  const parts = str.split(':')
  if (parts.length === 3) {
    // 确保 ContentName 只能是 'Payloads' 或 'Results'
    const contentName = parts[1] as 'Payloads' | 'Results'
    if (contentName !== 'Payloads' && contentName !== 'Results') {
      return null
    }

    return {
      Nid: parts[0],
      Path: {
        ContentName: contentName,
        ContentId: parts[2],
      },
    }
  }
  return null
}

// 检查值是否为 RefVarItem 类型
const isRefVarItem = (value: any): value is RefVarItem => {
  return (
    value &&
    typeof value === 'object' &&
    'Nid' in value &&
    'Path' in value &&
    typeof value.Path === 'object' &&
    'ContentName' in value.Path &&
    'ContentId' in value.Path
  )
}

// 计算属性：将 RefVarItem 转换为 n-select 需要的字符串值
const computedValue = computed({
  get: () => {
    if (!props.value) return null

    // 如果已经是字符串，直接返回
    if (typeof props.value === 'string') {
      return props.value
    }

    // 如果是 RefVarItem，转换为字符串
    if (isRefVarItem(props.value)) {
      return refVarItemToString(props.value)
    }

    return null
  },
  set: (val) => {
    updateValue(val)
  },
})

// 计算属性：将 RefVarItem 数组转换为 n-select 需要的选项格式
const computedOptions = computed(() => {
  return props.options.map((refItem) => {
    const itemstr = refVarItemToString(refItem)
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

  // 尝试将字符串转换为 RefVarItem
  const refItem = stringToRefVarItem(value)

  // 如果能成功转换为 RefVarItem，则发送 RefVarItem
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

    // 如果标签不是 RefVarItem 格式（不包含两个冒号），直接显示标签
    if (!option.label.includes(':') || option.label.split(':').length !== 3) {
      throw new Error('Invalid label format')
    }

    const [nid, contentName, contentId] = option.label.split(':')
    const node = findNode(nid) as NodeWithVFData

    // 如果找不到节点，直接显示原始标签
    if (!node) {
      throw new Error(`Cannot find node with nid: ${nid}`)
    }

    const nLabel = node?.data.Label
    // 确保 contentName 是有效的 ('Payloads' 或 'Results')
    if (contentName !== 'Payloads' && contentName !== 'Results') {
      throw new Error(`Invalid contentName: ${contentName}`)
    }

    // 安全地访问数据
    const contentData = node?.data[contentName]?.ById?.[contentId]
    if (!contentData) {
      throw new Error(`Cannot find data for ${contentName}:${contentId}`)
    }

    const dLabel = contentData.Label
    const dType = contentData.Type
    return [
      h(NText, { type: 'default', strong: true }, { default: () => `${nLabel}` }),
      h(NText, { type: 'default' }, { default: () => ' - ' }),
      h(NText, { type: 'info' }, { default: () => dLabel }),
      h(NText, { type: 'info', italic: true }, { default: () => ` ${dType}` }),
    ]
  } catch (e) {
    return h(NText, { type: 'error', strong: true }, { default: () => `❌${option.label}` })
  }
}
</script>
