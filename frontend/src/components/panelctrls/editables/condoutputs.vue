<template>
  <n-flex vertical>
    <!-- 添加条件分支按钮 -->
    <n-flex class="flexctitem" justify="space-between">
      <editable_header type="warning">分支设计</editable_header>
      <n-button type="warning" text @click="addBranch" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <Add />
          </n-icon>
        </template>
        新增分支
      </n-button>
    </n-flex>

    <!-- 条件分支列表 -->
    <n-card v-for="(branch, bindex) in branches" :key="branch.rid">
      <template #header>
        <n-flex class="flexctitem" justify="flex-start">
          <n-text> {{ branch.data.label }} </n-text>
        </n-flex>
      </template>
      <template #header-extra>
        <n-switch
          v-if="branch.data.data.conditions.length > 1"
          :value="branch.data.data.condType === 'AND'"
          @update:value="(val) => updateCondType(branch.rid, val)"
          size="medium"
          :style="{ paddingRight: '40px' }"
          :rail-style="railStyle"
          :disabled="!isEditorMode"
        >
          <template #checked>AND</template>
          <template #unchecked>OR</template>
          <template #checked-icon>&</template>
          <template #unchecked-icon>|</template>
        </n-switch>
        <n-button
          circle
          tertiary
          type="error"
          @click="rmBranch(branch.rid)"
          :disabled="!isEditorMode"
        >
          <template #icon>
            <n-icon>
              <Close />
            </n-icon>
          </template>
        </n-button>
      </template>
      <n-card
        v-for="(cond, cindex) in branch.data.data.conditions"
        :key="cindex"
        hoverable
        size="small"
      >
        <n-flex class="flexctitem" :style="{ width: '100%' }" :wrap="false">
          <n-flex vertical :style="{ width: '90%' }">
            <n-flex :wrap="false">
              <cp_var_select
                :style="{ width: '65%' }"
                v-model:value="cond.refdata"
                :options="selfVarSelections"
                placeholder="变量"
              />
              <n-select
                :style="{ width: '35%' }"
                size="small"
                placeholder="操作"
                :disabled="!isEditorMode"
                :options="buildOpTypeSelections(cond.refdata)"
                v-model:value="cond.operator"
              />
            </n-flex>
            <n-flex :wrap="false">
              <n-select
                :style="{ width: '35%' }"
                size="small"
                placeholder="类型"
                :disabled="!isEditorMode"
                :options="VariableTypeSelectionsWRef"
                v-model:value="cond.comparetype"
              />
              <cp_var_input_type
                :style="{ width: '65%' }"
                :itemType="cond.comparetype"
                v-model:itemValue="cond.value"
                :selfVarSelections="selfVarSelections"
              />
            </n-flex>
          </n-flex>
          <n-button
            circle
            tertiary
            size="small"
            type="error"
            @click="rmCondition(branch.rid, cindex)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <Close />
              </n-icon>
            </template>
          </n-button>
        </n-flex>
      </n-card>
      <n-button text type="info" @click="addCondition(branch.rid)" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <Add />
          </n-icon>
        </template>
        新增条件
      </n-button>
    </n-card>
  </n-flex>
</template>

<script setup lang="ts">
import type { CSSProperties } from 'vue'
import { ref, computed, h, inject, defineAsyncComponent } from 'vue'
import {
  useMessage,
  NSwitch,
  NFlex,
  NText,
  NIcon,
  NButton,
  NCard,
  NInput,
  NSelect,
  type SelectOption,
} from 'naive-ui'
import { Add, Close } from '@vicons/ionicons5'
import { useVueFlow } from '@vue-flow/core'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import { getUuid } from '@/utils/tools'
import { isEditorMode } from '@/hooks/useVFlowAttribute'
import type { CondBranchDict, CondBranchData } from '@/schemas/cond_branch'
import { VariableTypeSelectionsWRef } from '@/schemas/select_schemas'
import {
  type VFNodeData,
  VFNodeConnectionType,
  VFNodeConnectionDataType,
} from '@/components/nodes/VFNodeInterface'
import {
  StartEndTypeSelections,
  EqualTypeSelections,
  ContainsTypeSelections,
  LengthTypeSelections,
  NullTypeSelections,
  NotEuqalTypeSelections,
  BooleanTypeSelections,
} from '@/schemas/cond_branch'
const cp_var_select = defineAsyncComponent(() => import('./common/var_select.vue'))
const cp_var_input_type = defineAsyncComponent(() => import('./common/var_input_type.vue'))

const props = defineProps<{
  selfVarSelections: SelectOption[]
}>()
// 获取节点数据
const { findNode, getHandleConnections, updateNodeInternals, removeEdges, getEdges } = useVueFlow()

const { curSelectedNode } = useCurSelectedNode()

const railStyle = ({ focused, checked }: { focused: boolean; checked: boolean }) => {
  let style: CSSProperties = {
    background: '#2080f0',
  }
  return style
}
interface Branch {
  rid: string
  data: CondBranchDict
}
const branches = computed<Branch[]>(() => {
  const conddata: Branch[] = []
  for (const rid of curSelectedNode.value.data.results.order) {
    if (curSelectedNode.value.data.results.byId[rid].key !== 'cond-else') {
      conddata.push({ rid, data: curSelectedNode.value.data.results.byId[rid] })
    }
  }
  return conddata
})

const updateOutputsLabel = () => {
  const elsekey = Object.keys(curSelectedNode.value.data.connections.outputs).filter((key) =>
    curSelectedNode.value.data.connections.outputs[key].label.endsWith('ELSE'),
  )
  curSelectedNode.value.data.connections.outputs[elsekey[0]].label =
    `${Object.keys(curSelectedNode.value.data.connections.outputs).length}/ELSE`
  const hids = Object.keys(curSelectedNode.value.data.connections.outputs).filter(
    (key) => !curSelectedNode.value.data.connections.outputs[key].label.endsWith('ELSE'),
  )
  for (let index = 0; index < hids.length; index++) {
    const hid = hids[index]
    curSelectedNode.value.data.connections.outputs[hid].label = `${index + 1}/CASE ${index + 1}`
    const rid = hid.replace('output-', '')
    curSelectedNode.value.data.results.byId[rid].label = `CASE ${index + 1}`
  }
}

const addBranch = () => {
  const bid = getUuid()
  const hid = `output-${bid}`
  const cid = `c-${bid}`
  const newBranch = {
    label: '-',
    type: 'ConditionDict',
    key: `cond-${bid}`,
    data: {
      outputKey: hid,
      condType: 'AND',
      conditions: [
        // 创建时默认存在一个
        {
          refdata: '',
          operator: 'eq',
          comparetype: 'Ref',
          value: '',
        } as CondBranchData,
      ],
    },
  }
  curSelectedNode.value.data.addResult(newBranch, bid)
  curSelectedNode.value.data.addHandle(VFNodeConnectionType.outputs, hid, '分支')
  curSelectedNode.value.data.addHandleData(
    VFNodeConnectionType.outputs,
    hid,
    { type: VFNodeConnectionDataType.FromOuter, inputKey: 'input-var' },
    cid,
  )
  updateNodeInternals([curSelectedNode.value.id])
  updateOutputsLabel()
}

const rmBranch = (rid: string) => {
  const hid = `output-${rid}`
  const cid = `c-${rid}`
  curSelectedNode.value.data.rmResult(rid)
  curSelectedNode.value.data.rmHandleData(VFNodeConnectionType.outputs, hid, cid)
  // 在去掉handle之前，还需要搜索并去掉对应的edges
  const edges = getHandleConnections({ id: hid, type: 'source', nodeId: curSelectedNode.value.id })
  removeEdges(edges.map((edge) => edge.edgeId))
  curSelectedNode.value.data.rmHandle(VFNodeConnectionType.outputs, hid)
  updateOutputsLabel()
}

const addCondition = (rid: string) => {
  const newCond: CondBranchData = {
    refdata: '',
    operator: 'eq',
    comparetype: 'Ref',
    value: '',
  }
  curSelectedNode.value.data.results.byId[rid].data.conditions.push(newCond)
}

const rmCondition = (rid: string, cindex: number) => {
  curSelectedNode.value.data.results.byId[rid].data.conditions.splice(cindex, 1)
}

// 更新条件类型(AND/OR)
const updateCondType = (rid: string, value: boolean) => {
  curSelectedNode.value.data.results.byId[rid].data.condType = value ? 'AND' : 'OR'
}

const buildOpTypeSelections = (refdata: string) => {
  const [nid, r_content, rid] = refdata.split('/')
  const thenode = findNode(nid)
  if (!thenode) {
    return [{ label: '×不支持', value: 'unsupported' }]
  }
  const rtype = thenode.data[r_content].byId[rid].type
  if (rtype === 'String') {
    return [
      ...StartEndTypeSelections,
      ...EqualTypeSelections,
      ...ContainsTypeSelections,
      ...LengthTypeSelections,
      ...NullTypeSelections,
    ]
  } else if (rtype === 'Integer' || rtype === 'Number') {
    return [...EqualTypeSelections, ...NotEuqalTypeSelections, ...NullTypeSelections]
  } else if (rtype === 'Boolean') {
    return [...EqualTypeSelections, ...BooleanTypeSelections, ...NullTypeSelections]
  } else if (rtype === 'List') {
    return [...ContainsTypeSelections, ...LengthTypeSelections, ...NullTypeSelections]
  } else {
    return [...NullTypeSelections]
  }
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
