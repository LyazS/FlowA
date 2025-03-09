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
  const node = new VFNode('LLM_inference', 'basenode', 'LLM推理')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
  node.addHandle(VFNodeConnectionType.outputs, 'output')

  node.addHandleData(VFNodeConnectionType.self, 'self', {
    type: VFNodeConnectionDataType.FromOuter,
    inputKey: 'input',
  })

  node.addPayload(
    {
      label: '模型设置',
      type: 'LLMModel',
      key: 'modelconfig',
      data: {
        model: { type: 'Value', value: 'deepseek-ai/DeepSeek-V2.5' },
        stream: true,
        max_tokens: { type: 'Null', value: 4096 },
        temperature: { type: 'Null', value: 0.75 },
        top_p: { type: 'Null', value: 0.9 },
        // top_k: { type: "null", value: 50 },
        frequency_penalty: { type: 'Null', value: 0.5 },
        response_format: { type: 'Null', value: 'json' }, // json
        stop: { type: 'Null', value: null }, // string|string[]|null
      },
      uitype: 'llmmodel',
    },
    'D_MODELCONFIG',
  )
  node.addPayload(
    {
      label: '输入变量',
      type: 'VarsInput',
      key: 'inputvars',
      data: [
        { key: 'text', type: 'String', value: 'good assistant' },
        { key: 'ask', type: 'String', value: 'hi' },
      ],
      uitype: 'vars_input',
    },
    'D_VARSINPUT',
  )

  node.addPayload(
    {
      label: 'LLMPrompts',
      type: 'Prompts',
      key: 'prompts',
      data: [
        { role: 'system', content: 'You are a {{text}}.' },
        { role: 'user', content: '{{ask}}' },
        // {
        //     "role": "user",
        //     "content":[
        //         {
        //             "type": "image_url",
        //             "image_url": {
        //                 "url": "https://xxx.png",
        //                 "detail":"high",
        //             }
        //         },
        //         {
        //             "type": "image_url",
        //             "image_url": {
        //                 "url": "data:image/png;base64,{base64_image}",
        //                 "detail":"low",
        //             }
        //         },
        //         {
        //             "type": "text",
        //             "text": "text-prompt here"
        //         }
        //     ]
        // },
      ],
      uitype: 'llmprompts',
    },
    'D_PROMPTS',
  )
  node.addResultWithConnection(
    { label: '推理结果', type: 'String', key: 'answer', data: '' },
    'output',
    'D_ANSWER',
  )
  node.addResultWithConnection(
    { label: 'LLM模型', type: 'String', key: 'model', data: '' },
    'output',
    'D_MODEL',
  )
  node.addResultWithConnection(
    { label: '输入Token', type: 'Integer', key: 'input_token', data: 0 },
    'output',
    'D_IN_TOKEN',
  )
  node.addResultWithConnection(
    { label: '输出Token', type: 'Integer', key: 'output_token', data: 0 },
    'output',
    'D_OUT_TOKEN',
  )
  node.addResultWithConnection(
    { label: '停止原因', type: 'String', key: 'stop_reason', data: '' },
    'output',
    'D_STOP_REASON',
  )

  node.setOutputsUIType('tagoutputs')
  return node
}
