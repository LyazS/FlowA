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
  const node = new VFNode('code_interpreter', 'basenode', '代码解释器')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
  node.addHandle(VFNodeConnectionType.outputs, 'output')
  // node.addHandle(VFNodeConnectionType.callbackUsers, 'callbackUser')
  // node.addHandle(VFNodeConnectionType.callbackFuncs, 'callbackFunc')
  node.addHandleData(VFNodeConnectionType.self, 'self', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input',
  })

  node.addPayload(
    {
      label: '输入变量',
      type: 'VarsInput',
      key: 'inputvars',
      data: [
        { key: 'arg1', type: 'String', value: 'hello' },
        { key: 'arg2', type: 'String', value: 'world' },
      ],
      uitype: 'vars_input',
    },
    'D_VARSINPUT',
  )
  node.addPayload(
    {
      label: 'Python 代码',
      type: 'String',
      key: 'Code',
      data: '#You can use numpy and cv2 by import\ndef main(arg1, arg2):\n    # do something\n    return {\n        "output1": arg1,\n        "output2": arg2\n    }',
      uitype: 'codeeditor',
      config: { language: 'python' },
    },
    'D_CODE',
  )

  node.addResultWithConnection(
    { label: 'output1', type: 'String', key: 'output1', data: null },
    'output',
  )
  node.addResultWithConnection(
    { label: 'output2', type: 'String', key: 'output2', data: null },
    'output',
  )

  node.setOutputsUIType('codeoutputs')
  return node
}
