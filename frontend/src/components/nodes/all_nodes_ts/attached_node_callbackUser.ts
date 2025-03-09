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
    'attached_node_callbackUser',
    'attached_node',
    '附属节点',
  ).initAsAttachedNode(
    VFNodeAttachingType.callbackUser,
    [VFNodeAttachingPos.top, 0, VFNodeAttachingPos.right, 0],
    'CB-USE',
  )
  node.setNodeFlag(VFNodeFlag.isAttached).setSize(20, 6)

  return node
}
