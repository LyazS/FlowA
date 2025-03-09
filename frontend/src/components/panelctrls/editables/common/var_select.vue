<template>
  <n-select
    :style="style"
    :value="value"
    @update:value="updateValue"
    :options="options"
    :render-label="renderLabel"
    :disabled="!isEditorMode"
    :size="size"
    :placeholder="placeholder"
    :consistent-menu-width="false"
    placement="bottom-end"
  />
</template>

<script setup lang="ts">
import { h } from 'vue'
import { NSelect, NText } from 'naive-ui'
import type { SelectOption } from 'naive-ui'
import { isEditorMode } from '@/hooks/useVFlowAttribute'
import { isString } from '@/utils/tools'

const props = withDefaults(
  defineProps<{
    value: string | undefined | null
    options: SelectOption[]
    size?: 'tiny' | 'small' | 'medium' | 'large'
    style?: Record<string, string | number>
    placeholder?: string
  }>(),
  {
    size: 'small',
    style: () => ({}),
    placeholder: '请选择',
  },
)

const emit = defineEmits<{
  'update:value': [value: string]
}>()

// 更新值的方法
const updateValue = (value: string): void => {
  emit('update:value', value)
}

const renderLabel = (option: SelectOption) => {
  try {
    if (!isString(option.label)) {
      throw new TypeError('label must be a string')
    }
    const isError = !props.options.some((select) => select.value === option.value)
    if (isError) {
      throw new Error('value not in options')
    }
    const [nlabel, dlabel, dkey, dtype] = option.label.split('/')
    return [
      h(NText, { type: 'default', strong: true }, { default: () => `${nlabel}` }),
      h(NText, { type: 'default' }, { default: () => '/ ' }),
      h(NText, { type: 'info' }, { default: () => dlabel }),
      h(NText, { type: 'info' }, { default: () => ` ${dtype}` }),
    ]
  } catch (e) {
    // console.warn(e);
    return h(NText, { type: 'error', strong: true }, { default: () => `❓${option.label}` })
  }
}
</script>
