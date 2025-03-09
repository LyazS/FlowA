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
  const node = new VFNode('jinja2_template', 'basenode', 'Jinja2模板')
  node.setNodeFlag(VFNodeFlag.isPassive).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
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
      label: 'Jinja2 模板',
      type: 'String',
      key: 'Code',
      data: '<p>{{ arg1 }}</p>\n<hr>\n<p>{{ arg2 }}</p>',
      uitype: 'codeeditor',
      config: { language: 'django' },
    },
    'D_CODE',
  )

  return node
}
