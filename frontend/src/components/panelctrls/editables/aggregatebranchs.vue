<template>
  <n-flex vertical>
    <editable_header type="warning">聚合设计</editable_header>
    <VueDraggable
      ghostClass="ghost"
      :animation="150"
      v-model="branchesData"
      :disabled="!isEditorMode"
    >
      <n-flex
        v-for="(item, index) in branchesData"
        :key="item.key"
        :style="{ flexWrap: 'nowrap', paddingBottom: '5px', alignItems: 'center' }"
      >
        <n-icon size="16">
          <EllipsisVerticalIcon />
        </n-icon>
        <n-select
          :style="{ width: '40%' }"
          size="small"
          :options="inputNodesOptions"
          :disabled="!isEditorMode"
          v-model:value="item.node"
        />
        <cp_var_select
          :style="{ width: '60%' }"
          v-model:value="item.refdata"
          :options="getBuildNodeOutVars(item.node)"
        />
        <n-button circle tertiary type="error" @click="removeVar(index)" :disabled="!isEditorMode">
          <template #icon>
            <n-icon>
              <CloseIcon />
            </n-icon>
          </template>
        </n-button>
      </n-flex>
    </VueDraggable>
    <n-flex justify="flex-start">
      <n-button text type="warning" @click="addVar" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <AddIcon />
          </n-icon>
        </template>
        添加分支变量
      </n-button>
    </n-flex>
  </n-flex>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineAsyncComponent } from 'vue'
import { NFlex, NIcon, NSelect, NButton } from 'naive-ui'
import {
  Add as AddIcon,
  Close as CloseIcon,
  EllipsisVertical as EllipsisVerticalIcon,
} from '@vicons/ionicons5'
import { useVueFlow } from '@vue-flow/core'
import editable_header from './common/header.vue'
import { getUuid } from '@/utils/tools'
import { VueDraggable } from 'vue-draggable-plus'
import { isEditorMode } from '@/hooks/useVFlowAttribute'
import { useNodeUtils } from '@/hooks/useNodeUtils'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import type { AggregateBranchData } from '@/schemas/branch_aggregate'
import type { InputNode } from '@/schemas/schemas'

const cp_var_select = defineAsyncComponent(() => import('./common/var_select.vue'))

const props = defineProps<{
  pid: string
  selfVarSelections: any[]
  inputNodes: Record<string, InputNode[]>
}>()

const { recursiveFindVariables, mapVarItemToSelect } = useNodeUtils()
const { findNode } = useVueFlow()
const { curSelectedNode } = useCurSelectedNode()

const branchesData = computed({
  get(): AggregateBranchData[] {
    return curSelectedNode.value.data.payloads.byId[props.pid].data
  },
  set(value: AggregateBranchData[]) {
    curSelectedNode.value.data.payloads.byId[props.pid].data = value
  },
})

const inputNodesOptions = computed(() => {
  const options: { label: string; value: string }[] = []
  if (!props.inputNodes.input) return options
  for (const node of props.inputNodes.input) {
    const nid = node.srcid
    const thenode = findNode(nid)
    if (thenode) {
      let olabel = thenode.data.connections.outputs[node.srcohid].label
      const pattern = /^\d+\/[^/]*$/
      if (pattern.test(olabel)) {
        olabel = olabel.split('/')[1]
      }
      options.push({
        label: `${thenode.data.label}-${olabel.toUpperCase()}`,
        value: `${nid}/${node.srcohid}`,
      })
    }
  }
  return options
})

const getBuildNodeOutVars = (nid_ohid: string) => {
  const [nid, ohid] = nid_ohid.split('/')
  const node = findNode(nid)
  if (!node) return []
  return recursiveFindVariables(nid, [], [], [], false, [], false, [ohid]).map(mapVarItemToSelect)
}

const addVar = () => {
  branchesData.value.push({ node: '', refdata: '', key: getUuid() })
}

const removeVar = (index: number) => {
  branchesData.value.splice(index, 1)
}

watch(
  () => branchesData.value,
  (newLists: AggregateBranchData[]) => {
    if (Array.isArray(newLists) && newLists.length > 0) {
      const firstElement = newLists[0]
      if (firstElement.refdata) {
        const [nid, dpath, rid] = firstElement.refdata.split('/')
        const node = findNode(nid)

        if (curSelectedNode.value) {
          curSelectedNode.value.data.results.byId['D_OUTPUT'].type =
            node?.data[dpath]?.byId[rid]?.type
        }
      }
    }
  },
  { immediate: true, deep: true },
)
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}

.ghost {
  opacity: 0.5;
  background: #8e9192;
}
</style>
