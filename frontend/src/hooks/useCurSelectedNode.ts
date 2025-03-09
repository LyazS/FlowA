import { computed, type ComputedRef } from 'vue'
import type { NodeWithVFData } from '@/schemas/schemas'
import { selectedNodeId } from '@/hooks/useVFlowAttribute'
import { useVueFlow } from '@vue-flow/core'

interface CurNodeInstance {
  curSelectedNode: ComputedRef<NodeWithVFData>
}
let instance: CurNodeInstance | null = null
export const useCurSelectedNode = () => {
  if (instance) return instance
  const { findNode } = useVueFlow()

  const curSelectedNode = computed(() => {
    const node = findNode(selectedNodeId.value)
    if (node && node.data) return node as NodeWithVFData
    return null
  }) as ComputedRef<NodeWithVFData>

  instance = {
    curSelectedNode,
  }

  return instance
}
