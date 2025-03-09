<template>
  <n-modal :show="isShowJinja2Render" :close-on-esc="false" transform-origin="center">
    <n-card closable @close="isShowJinja2Render = false" class="fullscreen-card">
      <template #header>
        <editable_header type="success" :level="5"> Jinja2模板渲染 </editable_header>
      </template>
      <template #header-extra>
        <n-button @click="showSelectPanel = true" quaternary round type="info"> 节点选择 </n-button>
      </template>
      <n-flex justify="space-between">
        <template v-for="(value, nid) in Jinja2RenderData" :key="nid">
          <n-flex vertical style="flex: 1">
            <n-tag :bordered="false" type="warning">{{ value.label }}</n-tag>
            <n-scrollbar class="scrollable-content">
              <div v-if="value.rendered" v-html="value.rendered" class="scrollable-content" />
            </n-scrollbar>
          </n-flex>
        </template>
      </n-flex>
    </n-card>
  </n-modal>
  <n-modal v-model:show="showSelectPanel">
    <n-card closable @close="showSelectPanel = false" :style="{ width: '60%', maxWidth: '1000px' }">
      <n-transfer
        v-model:value="Jinja2RenderNodeIDs"
        :options="Jinja2NodeOptions"
        @update:value="Jinja2RenderNodeChange"
        size="large"
      />
    </n-card>
  </n-modal>
</template>

<script setup lang="ts">
import { type Ref, ref, onMounted, reactive, inject, computed, watch, onUnmounted } from 'vue'
import { type EventSourceMessage } from '@microsoft/fetch-event-source'
import { useVueFlow } from '@vue-flow/core'
import {
  useDialog,
  NText,
  NButton,
  NIcon,
  NButtonGroup,
  NScrollbar,
  NModal,
  NCard,
  NCollapse,
  NCollapseItem,
  NFlex,
  NGrid,
  NGridItem,
  NDivider,
  NEllipsis,
  NUpload,
  NTransfer,
  NTag,
} from 'naive-ui'
import editable_header from '@/components/panelctrls/editables/common/header.vue'
import { debounce, throttle } from 'lodash'
import {
  isEditing,
  isShowJinja2Render,
  Jinja2RenderNodeIDs,
  WorkflowID,
} from '@/hooks/useVFlowAttribute'
import { SubscribeSSE } from '@/utils/SSEMethod.ts'
import type { NodeWithVFData } from '@/schemas/schemas'
import type {
  FANodeUpdateData,
  SSEResponseData,
  FAWorkflowInfo,
  FAReleaseWorkflowInfo,
  JinjaRefTriggerData,
} from '@/schemas/vflow_schemas'
import { FAProgressRequestType } from '@/schemas/vflow_schemas'

// 类型定义
interface Jinja2RenderDataItem {
  label: string
  template: string
  content: Record<string, any>
  rendered: string | null
  isdirty: boolean
}

interface WorkerMessage {
  nid: string
  success: boolean
  rendered?: string
  error?: string
}

// Vue Flow 相关
const { findNode, getNodes } = useVueFlow()
const showSelectPanel = ref(false)
// 计算属性
const Jinja2NodeOptions = computed(() => {
  return getNodes.value
    .filter((node: NodeWithVFData) => node.data.ntype === 'jinja2_template')
    .map((node: NodeWithVFData) => ({
      label: node.data.label,
      value: node.id,
    }))
})

// 响应式数据
const Jinja2RenderData = ref<Record<string, Jinja2RenderDataItem>>({})

// Web Worker 处理
const worker = new Worker(new URL('@/utils/Jinja2RenderWoker.ts', import.meta.url), {
  type: 'module',
})

worker.onmessage = function (event: MessageEvent<WorkerMessage>) {
  const { nid, success, rendered, error } = event.data
  if (!success) {
    console.error('Template rendering failed:', error)
    return
  }

  if (Jinja2RenderData.value[nid]) {
    Jinja2RenderData.value[nid].rendered = rendered || null
    Jinja2RenderData.value[nid].isdirty = false
  }
}

// 节流函数
const Jinja2RenderUseWorker = throttle(() => {
  const tasks = Object.entries(Jinja2RenderData.value)
    .map(([nid, { template, content, isdirty }]) => {
      if (isdirty) {
        return {
          nid,
          template,
          content: JSON.parse(JSON.stringify(content)),
        }
      }
      return undefined
    })
    .filter(Boolean)

  if (tasks.length > 0) {
    worker.postMessage({ tasks })
  }
}, 300)

// SSE 处理
const { subscribe: subscribeJinja, unsubscribe: unsubscribeJinja } = SubscribeSSE(
  async (response: Response) => {
    console.log('onopen SSE Jinja2', response.ok)
  },
  (event: EventSourceMessage) => {
    if (!event.event || event.event === 'flowfinish') {
      return
    }
    const lines: SSEResponseData<JinjaRefTriggerData>[] = []

    let data
    try {
      data = JSON.parse(event.data)
    } catch (error) {
      console.error('JSON 解析失败:', error)
      console.error('无效的 JSON 输入:', event.data)
      return // 防止后续代码因 data 无效而崩溃
    }

    if (event.event === 'batchupdatenode') {
      lines.push(...data)
    } else if (event.event === 'updatenode') {
      lines.push(data)
    }

    for (const line of lines) {
      try {
        const { nid, data: updateDatas } = line
        if (!Jinja2RenderData.value[nid]) continue

        Jinja2RenderData.value[nid].isdirty = true

        updateDatas.forEach((updateData) => {
          const { path, operation, new_value, old_value } = updateData.data!
          let current = Jinja2RenderData.value[nid].content
          const combinedPath = [...updateData.path!, ...path]

          for (let i = 0; i < combinedPath.length - 1; i++) {
            const key = combinedPath[i]
            current[key] = current[key] || {}
            current = current[key]
          }

          const lastKey = combinedPath[combinedPath.length - 1]
          switch (operation) {
            case 'set':
              current[lastKey] = new_value
              break
            case 'append':
              current[lastKey] = Array.isArray(current[lastKey])
                ? [...current[lastKey], new_value]
                : [new_value]
              break
          }
        })
      } catch (error) {
        console.error('Error processing update:', error)
      }
    }
    Jinja2RenderUseWorker()
  },
  () => {
    console.log('onclose SSE Jinja2')
  },
  (err: any) => {
    console.log('onerror SSE Jinja2', err)
  },
)

// 主要逻辑函数
const Jinja2RenderNodeChange = throttle(async () => {
  if (!isShowJinja2Render?.value) return

  unsubscribeJinja()
  const selectedNids: string[] = []
  Jinja2RenderData.value = {}

  for (const nid of Jinja2RenderNodeIDs.value) {
    const node = findNode(nid)
    if (!node) continue

    const content = node.data.payloads.byId.D_VARSINPUT.data.reduce(
      (acc: Record<string, null>, curr: { key: string }) => {
        acc[curr.key] = null
        return acc
      },
      {},
    )

    Jinja2RenderData.value[nid] = {
      label: node.data.label,
      template: node.data.payloads.byId.D_CODE.data,
      content,
      rendered: null,
      isdirty: false,
    }
    selectedNids.push(nid)
  }

  Jinja2RenderNodeIDs.value = selectedNids
  localStorage.setItem(`${WorkflowID.value}:Jinja2RenderNodeIDs`, JSON.stringify(selectedNids))

  if (selectedNids.length > 0) {
    subscribeJinja(`${import.meta.env.VITE_API_URL}/api/progress`, 'POST', null, {
      type: FAProgressRequestType.JinJa,
      wid: WorkflowID.value,
      selected_nids: selectedNids,
    })
  }
}, 1000)

// 生命周期
watch(isShowJinja2Render, (newVal, oldVal) => {
  if (newVal && !oldVal) {
    Jinja2RenderNodeChange()
  } else if (!newVal && oldVal) {
    unsubscribeJinja()
  }
})

onUnmounted(() => {
  unsubscribeJinja()
  worker.terminate()
})

// 样式部分保持不变
</script>

<style scoped>
.fullscreen-card {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  margin: 0;
  padding: 0;
}

.scrollable-content {
  max-height: calc(100vh - 120px);
}
</style>
