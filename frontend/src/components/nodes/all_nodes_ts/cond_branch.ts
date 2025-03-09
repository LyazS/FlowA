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
  const node = new VFNode('cond_branch', 'basenode', '条件分支')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input-cond', 'CONDITION')
  node.addHandle(VFNodeConnectionType.inputs, 'input-var', 'VARIABLE')
  node.addHandle(VFNodeConnectionType.outputs, 'output-else', '0/ELSE')
  node.addHandleData(VFNodeConnectionType.self, 'self', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input-cond',
  })

  node.addHandleData(VFNodeConnectionType.outputs, 'output-else', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input-var',
  })
  node.addResult({ label: '其他', type: 'ConditionDict', key: 'cond-else', data: {} })

  node.setOutputsUIType('condoutputs')
  return node
}
