<template>
  <div :style="{ width: '100%', height: '100%', position: 'relative' }">
    <template v-for="(handle, index) in inputHandles" :key="handle.key">
      <Handle
        :id="handle.key"
        class="vue-flow__handle-input"
        type="target"
        :position="Position.Left"
        :style="{
          top: `${handle_h_pad + index * handle_h_gap}px`,
          left: `${handle_h_pad}px`,
          transform: 'translateY(0)',
        }"
      />
      <div
        class="corner-text"
        :style="{
          top: `${handle_h_pad + index * handle_h_gap}px`,
          left: `${handle_h_pad + handle_text_edge_pad}px`,
          transform: 'translateY(-1px)',
        }"
      >
        {{ handle.label }}
      </div>
    </template>

    <template v-for="(handle, index) in outputHandles" :key="handle.key">
      <Handle
        :id="handle.key"
        class="vue-flow__handle-output"
        type="source"
        :position="Position.Right"
        :style="{
          top: 'auto',
          bottom: `${handle_h_pad + index * handle_h_gap}px`,
          right: `${handle_h_pad}px`,
          transform: 'translateY(0)',
        }"
      />
      <div
        class="corner-text"
        :style="{
          top: 'auto',
          bottom: `${handle_h_pad + index * handle_h_gap}px`,
          right: `${handle_h_pad + handle_text_edge_pad}px`,
          transform: 'translateY(1px)',
        }"
      >
        {{ handle.label }}
      </div>
    </template>

    <template v-for="(handle, index) in cbuserHandles" :key="handle.key">
      <Handle
        :id="handle.key"
        class="vue-flow__handle-callbackUser"
        type="source"
        :position="Position.Right"
        :style="{
          top: `${handle_h_pad + index * handle_h_gap}px`,
          right: `${handle_h_pad}px`,
          transform: 'translateY(0)',
        }"
      />
      <div
        class="corner-text"
        :style="{
          top: `${handle_h_pad + index * handle_h_gap}px`,
          right: `${handle_h_pad + handle_text_edge_pad}px`,
          transform: 'translateY(-1px)',
        }"
      >
        {{ handle.label }}
      </div>
    </template>

    <template v-for="(handle, index) in cbfuncHandles" :key="handle.key">
      <Handle
        :id="handle.key"
        class="vue-flow__handle-callbackFunc"
        type="target"
        :position="Position.Left"
        :style="{
          top: 'auto',
          bottom: `${handle_h_pad + index * handle_h_gap}px`,
          left: `${handle_h_pad}px`,
          transform: 'translateY(0)',
        }"
      />
      <div
        class="corner-text"
        :style="{
          top: 'auto',
          bottom: `${handle_h_pad + index * handle_h_gap}px`,
          left: `${handle_h_pad + handle_text_edge_pad}px`,
          transform: 'translateY(1px)',
        }"
      >
        {{ handle.label }}
      </div>
    </template>

    <div
      class="center-text"
      ref="hiddenText"
      :style="{
        position: 'absolute',
        top: `${center_text_pos.top}px`,
        left: '50%',
        transform: `translate(-50%, ${center_text_pos.trfY}%)`,
      }"
    >
      {{ thisnodedata.Label }}
    </div>
    <n-flex
      v-if="isShowCopyCount"
      justify="center"
      :style="{
        flexWrap: 'nowrap',
        position: 'absolute',
        top: `${center_text_pos.top}px`,
        left: '50%',
        transform: `translate(-50%,  ${center_text_pos.copCountY}%) translate(0,  10px)`,
      }"
    >
      <div class="state-text" style="color: #70c0e8">
        {{ thisnodedata.State!.CopyCount.Running }}
      </div>
      <div class="state-text" style="color: white">/</div>
      <div class="state-text" style="color: #63e2b7">
        {{ thisnodedata.State!.CopyCount.Success }}
      </div>
      <div class="state-text" style="color: white">/</div>
      <div class="state-text" style="color: #e88080">{{ thisnodedata.State!.CopyCount.Error }}</div>
    </n-flex>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, type Ref } from 'vue'
import { debounce } from 'lodash'
import { NFlex } from 'naive-ui'
import { Position, Handle, useVueFlow, type Node } from '@vue-flow/core'
import { VFNodeFlag } from '@/components/nodes/VFNodeInterface'
import { type VFNode } from '../VFNodeClass'

interface HandleData {
  key: string
  label: string
}

const props = defineProps<{
  id: string
}>()

const { findNode } = useVueFlow()
const thisnode = findNode(props.id) as Node
const thisnodedata = thisnode.data as VFNode

const handle_h_pad = 1
const handle_h_gap = 8
const handle_text_edge_pad = 6
const label_gap = 15

const inputHandles = computed<HandleData[]>(() => {
  const handles: HandleData[] = []
  const order = thisnodedata.Connections.Inputs.Order
  // 从前往后遍历
  for (let i = 0; i < order.length; i++) {
    const key = order[i]
    handles.push({
      key: key,
      label: thisnodedata.Connections.Inputs.ById[key].Label,
    })
  }
  return handles
})

const outputHandles = computed<HandleData[]>(() => {
  const handles: HandleData[] = []
  const order = thisnodedata.Connections.Outputs.Order
  // 从后往前遍历
  for (let i = order.length - 1; i >= 0; i--) {
    const key = order[i]
    handles.push({
      key: key,
      label: thisnodedata.Connections.Outputs.ById[key].Label,
    })
  }
  return handles
})

const cbfuncHandles = computed<HandleData[]>(() => {
  return Object.entries(thisnodedata.Connections.CallbackFuncs.ById)
    .map(([key, value]) => ({ key, label: value.Label }))
    .sort((a, b) => a.key.localeCompare(b.key))
})

const cbuserHandles = computed<HandleData[]>(() => {
  return Object.entries(thisnodedata.Connections.CallbackUsers.ById)
    .map(([key, value]) => ({ key, label: value.Label }))
    .sort((a, b) => a.key.localeCompare(b.key))
})

const max_handles_top = computed(() =>
  Math.max(inputHandles.value.length, cbuserHandles.value.length),
)

const max_handles_bottom = computed(() =>
  Math.max(outputHandles.value.length, cbfuncHandles.value.length),
)

const center_text_pos = computed(() => {
  return VFNodeFlag.IsNested & thisnodedata.Flag
    ? { top: 0, trfY: 0, copCountY: 50 }
    : {
        top: handle_h_pad + max_handles_top.value * handle_h_gap + 10,
        trfY: -50,
        copCountY: -50,
      }
})

const hiddenText: Ref<HTMLDivElement | null> = ref(null)

const isShowCopyCount = computed(() => Object.keys(thisnodedata.State.Copy).length > 0)

const countCopy = (statecopy: Record<string, { Status: string }>) => {
  let copyRunning = 0
  let copySuccess = 0
  let copyError = 0

  Object.values(statecopy).forEach((sc) => {
    if (sc.Status === 'Running' || sc.Status === 'Pending') {
      copyRunning++
    } else if (sc.Status === 'Success') {
      copySuccess++
    } else if (sc.Status === 'Error' || sc.Status === 'Canceled') {
      copyError++
    }
  })

  thisnodedata.State.CopyCount = {
    Running: copyRunning,
    Success: copySuccess,
    Error: copyError,
  }

  if (copyRunning > 0) {
    thisnodedata.State.Status = 'Running'
  } else if (copyError > 0) {
    thisnodedata.State.Status = 'Error'
  } else if (copySuccess > 0) {
    thisnodedata.State.Status = 'Success'
  } else {
    thisnodedata.State.Status = 'Default'
  }
}

const debouncedCountCopy = debounce(countCopy, 500)

onMounted(() => {
  watch(
    () => thisnodedata.State.Copy,
    (newValue) => {
      debouncedCountCopy(newValue)
    },
    { deep: true },
  )

  if (!thisnodedata.isNestedNode()) {
    watch(
      [max_handles_top, max_handles_bottom],
      ([newtop, newbottom]) => {
        const node_ht = 30 + (newtop + newbottom) * handle_h_gap
        thisnode.style = {
          ...thisnode.style,
          height: `${node_ht}px`,
        }
        thisnodedata.Size.Height = node_ht
      },
      { immediate: true },
    )

    watch(
      () => thisnodedata.Label,
      async (newLabel) => {
        await nextTick(() => {
          if (hiddenText.value && newLabel !== '') {
            const node_wd = hiddenText.value.offsetWidth + label_gap * 2
            thisnode.style = {
              ...thisnode.style,
              width: `${node_wd}px`,
            }
            thisnodedata.Size.Width = node_wd
          }
        })
      },
      { immediate: true },
    )

    watch(
      () => thisnodedata.State.Status,
      (newStatus) => {
        if (newStatus === 'Default') {
          if (thisnodedata.State.Errors.length > 0) {
            thisnode.class = 'node-status-invalid'
          } else {
            thisnode.class = 'node-status-default'
          }
        } else if (newStatus === 'Pending') {
          thisnode.class = 'node-status-pending'
        } else if (newStatus === 'Running') {
          thisnode.class = 'node-status-running'
        } else if (newStatus === 'Success') {
          thisnode.class = 'node-status-success'
        } else if (newStatus === 'Canceled') {
          thisnode.class = 'node-status-canceled'
        } else if (newStatus === 'Error') {
          thisnode.class = 'node-status-error'
        } else if (newStatus === 'Passive') {
          thisnode.class = 'node-status-passive'
        }
      },
      { immediate: true },
    )

    watch(
      () => thisnodedata.State.Errors,
      (newErrors) => {
        if (thisnodedata.State.Status === 'Default') {
          if (newErrors.length > 0) {
            thisnode.class = 'node-status-invalid'
          } else {
            thisnode.class = 'node-status-default'
          }
        }
      },
      { immediate: true },
    )
  }
})
</script>

<style>
.node-status-default,
.node-status-invalid,
.node-status-passive,
.node-status-pending,
.node-status-running,
.node-status-success,
.node-status-canceled,
.node-status-error {
  overflow: hidden;
}

.node-status-passive {
  background: linear-gradient(
    45deg,
    rgba(51, 33, 0, 0.8),
    rgba(102, 82, 39, 0.9),
    rgba(158, 135, 91, 0.95),
    rgba(102, 82, 39, 0.9),
    rgba(51, 33, 0, 0.8)
  );
  background-size: 300% 300%;
  animation: emeraldWave 8s ease infinite;
  backdrop-filter: brightness(1.1);
}

.node-status-passive.selected,
.node-status-passive:hover {
  --color: rgba(194, 168, 120, 0.8);
  border: 2px solid var(--color);
  box-shadow:
    0 0 12px rgba(194, 168, 120, 0.6),
    inset 0 0 4px 1px rgba(255, 235, 195, 0.3);
  transition:
    box-shadow 0.3s ease,
    border 0.3s ease;
}

.node-status-invalid {
  background: linear-gradient(45deg, #400000, #b71c1c, #ff4444, #b71c1c, #400000);
  background-size: 300% 300%;
  animation: emeraldWave 8s ease infinite;
}

.node-status-invalid.selected,
.node-status-invalid:hover {
  --color: #ff4444; /* 亮红色 */
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

.node-status-pending {
  background: linear-gradient(45deg, #2c3e50, #546e7a, #78909c, #546e7a, #2c3e50);
  background-size: 300% 300%;
  animation: emeraldWave 8s ease infinite;
}

.node-status-pending.selected,
.node-status-pending:hover {
  --color: #78909c;
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

.node-status-running {
  --c: #2196f3;
  --w1: radial-gradient(100% 57% at top, #0000 100%, var(--c) 100.5%) no-repeat;
  --w2: radial-gradient(100% 57% at bottom, var(--c) 100%, #0000 100.5%) no-repeat;
  background: var(--w1), var(--w2), var(--w1), var(--w2);
  background-position-x:
    -200%,
    -100%,
    0%,
    100%;
  background-position-y: 100%;
  background-size: 50.5% 100%;
  animation: wavewater 1s infinite linear;
}

@keyframes wavewater {
  0% {
    background-position-x:
      -200%,
      -100%,
      0%,
      100%;
  }

  100% {
    background-position-x: 0%, 100%, 200%, 300%;
  }
}

.node-status-running.selected,
.node-status-running:hover {
  --color: #2196f3d2;
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

.node-status-success {
  background: linear-gradient(45deg, #004d40, #00897b, #00bfa5, #00897b, #004d40);
  background-size: 300% 300%;
  animation: emeraldWave 8s ease infinite;
}

.node-status-success.selected,
.node-status-success:hover {
  --color: #00bfa5;
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

.node-status-canceled::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  height: 300%;
  background-image: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="10" height="20" fill="gray"/><text x="5" y="10" font-family="ui-monospace" font-size="3" fill="black" text-anchor="middle" dominant-baseline="middle" transform="translate(0, 0) rotate(90 5,10)">CANCELED</text></svg>');
  background-repeat: repeat;
  transform: translate(-50%, -50%) rotate(-135deg);
  animation: scrollBackground 60s linear infinite;
}

.node-status-canceled.selected,
.node-status-canceled:hover {
  --color: #5b5555;
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

.node-status-error::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  height: 300%;
  background-image: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="10" height="20" fill="red"/><text x="5" y="10" font-family="ui-monospace" font-size="4" font-weight="bold" fill="black" text-anchor="middle" dominant-baseline="middle" transform="translate(0, 0) rotate(90 5,10)">ERROR</text></svg>');
  background-repeat: repeat;
  transform: translate(-50%, -50%) rotate(-45deg);
  animation:
    scrollBackground 15s linear infinite,
    opacityBackground 3s cubic-bezier(0.2, 0.06, 0.17, 0.98) infinite;
}

.node-status-error.selected,
.node-status-error:hover {
  --color: #e43d3a;
  border: 2px solid var(--color);
  box-shadow:
    0 0 10px var(--color),
    inset 0 0 3px 1px var(--color);
  transition:
    box-shadow 0.2s ease,
    border 0.2s ease;
}

@keyframes emeraldWave {
  0% {
    background-position: 10% 50%;
  }

  50% {
    background-position: 90% 50%;
  }

  100% {
    background-position: 10% 50%;
  }
}

@keyframes scrollBackground {
  0% {
    background-position: 0 0;
  }

  100% {
    background-position: 120px 400px;
  }
}

@keyframes opacityBackground {
  0% {
    opacity: 0.1;
  }

  50% {
    opacity: 0.9;
  }

  100% {
    opacity: 0.1;
  }
}
</style>
<style scoped>
.layout-container {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: transparent;
}

.corner-text {
  text-transform: uppercase;
  font-size: 4px;
  color: white;
  font-family: var(--font-mono);
  letter-spacing: 0.1px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: absolute;
  display: flex;
  align-items: flex-end;
  text-align: center;
}

.center-text {
  font-size: 12px;
  color: white;
  letter-spacing: 0.1px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-wrap: nowrap;
}

.state-text {
  font-size: 6px;
  letter-spacing: 0.1px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-wrap: nowrap;
}

/* 隐藏用于测量的文字样式 */
.hidden {
  visibility: hidden;
  position: absolute;
  white-space: nowrap;
  pointer-events: none;
}
</style>
