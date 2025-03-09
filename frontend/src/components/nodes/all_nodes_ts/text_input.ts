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
  const node = new VFNode('text_input', 'basenode', '文本输入')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.outputs, 'output')

  let pid = node.addPayload({
    label: '文本内容',
    type: 'String',
    key: 'text',
    data: '',
    uitype: 'textinput',
  })
  node.addHandleData(VFNodeConnectionType.outputs, 'output', {
    type: VFNodeConnectionDataType.FromInner,
    path: ['payloads', pid],
  })
  node.setOutputsUIType('tagoutputs')
  return node
}
