import { ref } from 'vue'
import {
  VFNodeConnectionDataType,
  VFNodeConnectionDataAttachedType,
  VFNodeConnectionType,
  VFNodeFlag,
  VFNodeAttachingPos,
  VFNodeAttachingType,
} from '@/components/nodes/VFNodeInterface'
import { VFNode } from '@/components/nodes/VFNodeClass'
import NodeVue from '@/components/nodes/all_nodes_vue/attached_node.vue'
export { NodeVue }
export function createNode(): VFNode {
  const node = new VFNode(
    'attached_node_callbackFunc',
    'attached_node',
    '附属节点',
  ).initAsAttachedNode(
    VFNodeAttachingType.callbackFunc,
    [VFNodeAttachingPos.bottom, 0, VFNodeAttachingPos.left, 0],
    'CB-FUN',
  )
  node.setNodeFlag(VFNodeFlag.isAttached).setSize(20, 6)

  return node
}
