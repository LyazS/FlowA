<script setup lang="ts">
import { computed, provide, ref, h, watch, inject, onMounted, onUnmounted, nextTick } from 'vue'
import {
  useMessage,
  useDialog,
  darkTheme,
  NConfigProvider,
  NMessageProvider,
  NCard,
  NButton,
  NButtonGroup,
  NDropdown,
  NInput,
  NPopover,
  NFlex,
  NIcon,
  NEllipsis,
} from 'naive-ui'
import {
  AddSharp,
  Play,
  RemoveSharp,
  ScanSharp,
  RocketSharp,
  ArrowUndo,
  ArrowBack,
  GitCommit,
  PlayCircleOutline,
  Stop,
  DocumentText,
} from '@vicons/ionicons5'
import { useVFlowRequest } from '@/services/useVFlowRequest'
import {
  WorkflowModeType,
  selectedNodeId,
  isEditorMode,
  isShowCodeEditor,
  WorkflowID,
  WorkflowMode,
  ReleaseWorkflowID,
  ReleaseWorkflowName,
  WorkflowName,
  isShowVFlowMgr,
  isShowJinja2Render,
} from '@/hooks/useVFlowAttribute'
const { switchWorkflow, runflow, stopflow, loadReleaseWorkflow } = useVFlowRequest()

const message = useMessage()

const run_loading = ref<boolean>(false)
const runIncrementalFlowAction = async (): Promise<void> => {
  run_loading.value = true
  const res = await runflow('Incremental')
  run_loading.value = false
  if (res.type === 'success') {
    message.success('开始运行')
  } else {
    message.error(`运行失败：${res.message}`)
  }
}
const runFullFlowAction = async (): Promise<void> => {
  run_loading.value = true
  const res = await runflow('full')
  run_loading.value = false
  if (res.type === 'success') {
    message.success('开始运行')
  } else {
    message.error(`运行失败：${res.message}`)
  }
}
const loadReleaseWorkflowAction = async () => {
  const storeRWName = ReleaseWorkflowName.value
  const res = await loadReleaseWorkflow(WorkflowID.value, ReleaseWorkflowID.value)
  if (res.type === 'success') {
    isShowVFlowMgr.value = false
    message.success(`已加载版本【${storeRWName}】`)
  } else {
    message.error(`版本加载失败: ${res.message}`)
  }
}
</script>

<template>
  <n-flex justify="flex-end">
    <template v-if="WorkflowMode === WorkflowModeType.Edit">
      <n-popover trigger="hover">
        <template #trigger>
          <n-button
            class="glow-btn"
            round
            tertiary
            type="success"
            @click="runIncrementalFlowAction"
          >
            <template #icon>
              <n-icon>
                <RocketSharp />
              </n-icon>
            </template>
            运行
          </n-button>
        </template>
        <span>增量运行</span>
      </n-popover>
      <n-popover trigger="hover">
        <template #trigger>
          <n-button class="glow-btn" circle tertiary type="success" @click="runFullFlowAction">
            <template #icon>
              <n-icon>
                <PlayCircleOutline />
              </n-icon>
            </template>
          </n-button>
        </template>
        <span>全量运行</span>
      </n-popover>
    </template>
    <template v-else-if="WorkflowMode === WorkflowModeType.View">
      <n-popover trigger="hover">
        <template #trigger>
          <n-button class="glow-btn" round tertiary type="info" @click="switchWorkflow(WorkflowID)">
            <template #icon>
              <n-icon>
                <ArrowBack />
              </n-icon>
            </template>
            返回编辑
          </n-button>
        </template>
        <span>返回编辑界面</span>
      </n-popover>
      <n-popover trigger="hover">
        <template #trigger>
          <n-button
            class="glow-btn"
            round
            tertiary
            type="warning"
            @click="loadReleaseWorkflowAction()"
          >
            <template #icon>
              <n-icon>
                <GitCommit />
              </n-icon>
            </template>
            加载
          </n-button>
        </template>
        <span>⚠️⚠️⚠️将会覆盖掉当前的工作流⚠️⚠️⚠️</span>
      </n-popover>
    </template>
    <template v-else-if="WorkflowMode === WorkflowModeType.Run">
      <n-popover trigger="hover">
        <template #trigger>
          <n-button
            class="glow-btn"
            round
            tertiary
            type="warning"
            @click="isShowJinja2Render = true"
          >
            <template #icon>
              <n-icon>
                <DocumentText />
              </n-icon>
            </template>
            Jinja渲染
          </n-button>
        </template>
        <span>打开Jinja2渲染面板</span>
      </n-popover>
      <n-popover trigger="hover">
        <template #trigger>
          <n-button class="glow-btn" tertiary round type="error" @click="stopflow()">
            <template #icon>
              <n-icon>
                <Stop />
              </n-icon>
            </template>
            停止
          </n-button>
        </template>
        <span>中止运行</span>
      </n-popover>
    </template>
  </n-flex>
</template>

<style scoped></style>
