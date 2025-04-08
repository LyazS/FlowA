<script setup lang="ts">
import { computed, ref, watch, provide, defineAsyncComponent, inject } from 'vue'
import {
  useMessage,
  darkTheme,
  NConfigProvider,
  NMessageProvider,
  NCard,
  NButton,
  NFlex,
  NText,
  NSelect,
  NInputGroup,
  NInputGroupLabel,
  NEllipsis,
} from 'naive-ui'
import { Panel, useVueFlow } from '@vue-flow/core'
import {
  selectedNodeId,
  isEditorMode,
  isShowCodeEditor,
  isShowJinja2Render,
  AutoSaveMessage,
  WorkflowMode,
  WorkflowModeType,
} from '@/hooks/useVFlowAttribute'
import nodeAttribute from './nodeAttribute.vue'
import ctrlpanel from './ctrlpanel.vue'
import mgrpanel from './mgrpanel.vue'
import mappanel from './mappanel.vue'

const AceCodeEditor = defineAsyncComponent(() => import('./AceCodeEditor.vue'))
const vflowManager = defineAsyncComponent(() => import('./vflowManager.vue'))
const Jinja2Render = defineAsyncComponent(() => import('./Jinja2Render.vue'))
</script>

<template>
  <Panel position="top-left" :style="{ width: 'auto' }">
    <n-flex justify="flex-start">
      <n-text
        :style="{
          pointerEvents: 'none',
          userSelect: 'none',
          WebkitUserSelect: 'none',
        }"
        depth="3"
      >
        {{ AutoSaveMessage }}
      </n-text>
    </n-flex>
  </Panel>
  <Panel position="top-right" :style="{ width: 'auto' }">
    <mgrpanel />
  </Panel>
  <Panel position="bottom-left" :style="{ width: 'auto' }">
    <mappanel />
  </Panel>
  <Panel position="bottom-center" :style="{ width: 'auto' }">
    <ctrlpanel />
  </Panel>

  <Panel class="nodepanel" position="top-right">
    <nodeAttribute v-if="!!selectedNodeId" />
  </Panel>
  <AceCodeEditor />
  <vflowManager />
  <Jinja2Render v-if="WorkflowMode === WorkflowModeType.Run" />
</template>

<style scoped>
.nodepanel {
  margin-top: 65px;
  width: 600px;
  border-radius: 10px;
}

.nodepanel:hover {
  box-shadow: 0 0 20px rgb(138, 203, 236);
  transition: box-shadow 0.2s ease;
}
</style>
