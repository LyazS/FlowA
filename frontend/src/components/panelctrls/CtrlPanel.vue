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
  ReloadOutline,
  GitCommit,
  PlayCircleOutline,
  Stop,
  DocumentText,
  TrashOutline,
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
const { switchWorkflow, runflow,clearflowcache, stopflow, loadReleaseWorkflow } = useVFlowRequest()

const message = useMessage()

const run_loading = ref<boolean>(false)
const runFlowAction = async (): Promise<void> => {
  run_loading.value = true
  const res = await runflow()
  run_loading.value = false
  if (res.type === 'success') {
    message.success('开始运行')
  } else {
    message.error(`运行失败：${res.message}`)
  }
}
const clearFlowCacheAction = async (): Promise<void> => {
  run_loading.value = true
  const res = await clearflowcache()
  run_loading.value = false
  if (res.type === 'success') {
    message.success('清空缓存成功')
  } else {
    message.error(`清空缓存失败：${res.message}`)
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
            @click="runFlowAction"
          >
            <template #icon>
              <n-icon>
                <RocketSharp />
              </n-icon>
            </template>
            运行
          </n-button>
        </template>
        <span>运行当前工作流</span>
      </n-popover>
      <n-popover trigger="hover">
        <template #trigger>
          <n-button class="glow-btn" circle tertiary type="success" @click="clearFlowCacheAction">
            <template #icon>
              <n-icon>
                <TrashOutline />
              </n-icon>
            </template>
          </n-button>
        </template>
        <span>清空当前工作流缓存</span>
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
