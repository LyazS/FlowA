<script setup lang="ts">
import { NButton, NFlex, NIcon, NEllipsis } from 'naive-ui'
import { WorkflowName, isShowVFlowMgr } from '@/hooks/useVFlowAttribute'
</script>

<template>
  <n-flex justify="flex-end">
    <n-button
      class="glow-btn"
      round
      tertiary
      type="primary"
      style="min-width: 200px"
      @click="isShowVFlowMgr = true"
    >
      <n-ellipsis v-if="WorkflowName" style="max-width: 240px"> - {{ WorkflowName }} - </n-ellipsis>
      <n-ellipsis v-else style="max-width: 240px"> - 工作流管理器 - </n-ellipsis>
    </n-button>
  </n-flex>
</template>
<style scoped></style>
