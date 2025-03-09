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
  const node = new VFNode('iter_retry_run', 'basenode', '迭代重试').initAsNestedNode(null)
  node.setNodeFlag(VFNodeFlag.isTask | VFNodeFlag.isNested).setSize(200, 200)

  node.addAttachedNode(VFNodeConnectionDataAttachedType.attached_node_input)
  node.addAttachedNode(VFNodeConnectionDataAttachedType.attached_node_output)
  node.addAttachedNode(VFNodeConnectionDataAttachedType.attached_node_break)

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

  const pid = node.addPayload({
    label: '迭代项目',
    type: 'IterRetryItem',
    key: 'iter_item',
    data: null,
    uitype: 'texttag',
  })
  node.addHandleData(VFNodeConnectionType.attach, 'attach', {
    type: VFNodeConnectionDataType.FromInner,
    path: ['payloads', pid],
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
  node.addPayload(
    {
      label: '输入输出',
      type: 'Dict',
      key: 'retry_inout',
      data: {
        input: '',
        output: '',
      },
      uitype: 'iterretryoutputs',
    },
    'D_RETRY_INOUT',
  )
  node.addResultWithConnection(
    { label: '输出', type: 'String', key: 'output', data: '' },
    'output',
    'D_OUTPUT',
  )
  node.setOutputsUIType('tagoutputs')
  return node
}
