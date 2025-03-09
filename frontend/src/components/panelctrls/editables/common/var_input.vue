<template>
  <!-- 保持模板部分不变 -->
  <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
    <n-flex class="flexctitem" :style="{ width: '95%' }" :wrap="false">
      <!-- 变量名 -->
      <n-input
        :style="{ width: '30%' }"
        size="small"
        placeholder="变量名"
        :value="itemKey"
        :disabled="!isEditorMode"
        @blur="isEditing = false"
        @focus="isEditing = true"
        @update:value="updateKey"
      />
      <!-- 类型选择 -->
      <n-select
        :style="{ width: '20%' }"
        size="small"
        :options="VariableTypeSelectionsWRef"
        :disabled="!isEditorMode"
        :value="itemType"
        @update:value="updateType"
        :consistent-menu-width="false"
      />
      <!-- 值输入 -->
      <cp_var_input_type
        :style="{ width: '50%' }"
        size="small"
        :itemType="itemType"
        :itemValue="itemValue"
        :selfVarSelections="selfVarSelections"
        @update:itemValue="updateValue"
      />
    </n-flex>
    <!-- 删除按钮 -->
    <n-button circle tertiary size="small" type="error" @click="rmItem" :disabled="!isEditorMode">
      <template #icon>
        <n-icon>
          <Close />
        </n-icon>
      </template>
    </n-button>
  </n-flex>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import { NFlex, NIcon, NButton, NInput, NSelect, type SelectOption } from 'naive-ui'
import { Add, Close } from '@vicons/ionicons5'
import { isEditorMode, isEditing } from '@/hooks/useVFlowAttribute'
import type { AllVariableTypes, TSVariableType } from '@/schemas/select_schemas'
import { VariableTypeSelectionsWRef } from '@/schemas/select_schemas'

const cp_var_input_type = defineAsyncComponent(() => import('./var_input_type.vue'))

const props = defineProps<{
  itemKey: string
  itemType: AllVariableTypes
  itemValue: TSVariableType
  itemIdx: number
  selfVarSelections: SelectOption[]
}>()

const emit = defineEmits<{
  (e: 'update:itemKey', value: string): void
  (e: 'update:itemType', value: string): void
  (e: 'update:itemValue', value: TSVariableType): void
  (e: 'remove'): void
}>()

// 更新 key
const updateKey = (newKey: string) => {
  emit('update:itemKey', newKey)
}

// 更新 type
const updateType = (newType: string) => {
  emit('update:itemType', newType)
}

// 更新 value
const updateValue = (newValue: TSVariableType) => {
  emit('update:itemValue', newValue)
}

// 删除项
const rmItem = () => {
  emit('remove')
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
