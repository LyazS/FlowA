<template>
  <n-flex vertical>
    <editable_header>
      {{ curSelectedNode.data.payloads.byId[pid].label }}
    </editable_header>
    <n-input
      type="textarea"
      :autosize="{ minRows: 3, maxRows: 20 }"
      v-model:value="text_value"
      :disabled="!isEditorMode"
      @blur="isEditing = false"
      @focus="isEditing = true"
      placeholder="输入点内容吧"
    />
  </n-flex>
</template>

<style scoped></style>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { NInput, NFlex } from 'naive-ui'
import editable_header from './common/header.vue'
import { isEditorMode, isEditing } from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

const props = defineProps<{
  pid: string
}>()

const { curSelectedNode } = useCurSelectedNode()

const text_value = computed({
  get(): string {
    return curSelectedNode.value.data.payloads.byId[props.pid].data
  },
  set(new_val: string) {
    curSelectedNode.value.data.payloads.byId[props.pid].data = new_val
  },
})
</script>
