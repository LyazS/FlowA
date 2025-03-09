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
import NodeVue from '@/components/nodes/all_nodes_vue/basenode.vue'
export { NodeVue }
export function createNode(): VFNode {
  const node = new VFNode('retry_run', 'basenode', '重复重试').initAsNestedNode(null)
  node.setNodeFlag(VFNodeFlag.isTask | VFNodeFlag.isNested).setSize(200, 200)

  node.addAttachedNode(VFNodeConnectionDataAttachedType.attached_node_input)
  node.addAttachedNode(VFNodeConnectionDataAttachedType.attached_node_output)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
  node.addHandle(VFNodeConnectionType.outputs, 'output')
  node.addHandle(VFNodeConnectionType.self, 'attach_output')
  node.addHandleData(VFNodeConnectionType.self, 'self', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input',
  })
  node.addHandleData(VFNodeConnectionType.self, 'attach_output', {
    type: VFNodeConnectionDataType.FromAttached,
    atype: VFNodeConnectionDataAttachedType.attached_node_output,
  })
  node.addHandleData(VFNodeConnectionType.attach, 'attach', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input',
  })

  node.addPayload(
    {
      label: '重试设置',
      type: 'Dict',
      key: 'retry_config',
      data: {
        num_retries: 5,
        type: 'Immediate', // Immediate|Fixed|Exponential
        interval: 1000,
        exponential_base: 2.0,
        exponential_growth: 1.5,
      },
      uitype: 'retry_config',
    },
    'D_RETRY_CONFIG',
  )

  node.setOutputsUIType('retryoutputs')
  return node
}
