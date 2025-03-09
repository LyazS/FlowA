<script setup lang="ts">
import { ref, onMounted, reactive, inject, computed } from 'vue'
import { useVueFlow } from '@vue-flow/core'
import { NCode, NIcon, NButton, NFlex } from 'naive-ui'
import editable_header from './common/header.vue'
import { CreateOutline } from '@vicons/ionicons5'
import {
  selectedNodeId,
  isEditorMode,
  isEditing,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import type { CodeEditorLanguage } from '@/components/nodes/VFNodeInterface'

const props = defineProps<{
  pid: string
}>()

const { curSelectedNode } = useCurSelectedNode()

const thislang = computed<CodeEditorLanguage>(() => {
  return curSelectedNode.value.data.payloads.byId[props.pid].config!.language!
})

const editCode = (): void => {
  CodeEditorPath.value = ['data', 'payloads', 'byId', props.pid, 'data']
  CodeEditorLangType.value = thislang.value
  isShowCodeEditor.value = true
}
</script>

<template>
  <n-flex vertical>
    <n-flex class="flexctitem" justify="space-between">
      <editable_header type="warning">
        {{ curSelectedNode.data.payloads.byId[pid].label }}
      </editable_header>
      <n-button :disabled="!isEditorMode" text type="warning" @click="editCode">
        <template #icon>
          <n-icon>
            <CreateOutline />
          </n-icon>
        </template>
        放大编辑
      </n-button>
    </n-flex>
    <n-code
      :code="curSelectedNode.data.payloads.byId[pid].data"
      :language="thislang"
      show-line-numbers
      word-wrap
    />
  </n-flex>
</template>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
