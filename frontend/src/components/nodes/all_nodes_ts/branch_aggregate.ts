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
import type { AggregateBranchData } from '@/schemas/branch_aggregate'
export { NodeVue }

export function createNode(): VFNode {
  const node = new VFNode('branch_aggregate', 'basenode', '分支聚合')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
  node.addHandle(VFNodeConnectionType.outputs, 'output')

  node.addHandleData(VFNodeConnectionType.self, 'self', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input',
  })

  node.addPayload(
    {
      label: '聚合分支',
      type: 'AggregateBranch',
      key: 'branches',
      data: [
        // { node: "xxx/output", refdata: "", key: "uuid" },
        // { node: "nid/outputhid", refdata: "", key: "uuid" },
      ] as AggregateBranchData[],
      uitype: 'aggregatebranch',
    },
    'D_BRANCHES',
  )

  node.addResultWithConnection(
    { label: '输出变量', type: 'Value', key: 'output', data: null },
    'output',
    'D_OUTPUT',
  )

  node.setOutputsUIType('tagoutputs')
  return node
}
