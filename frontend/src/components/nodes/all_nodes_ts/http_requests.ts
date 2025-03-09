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
  const node = new VFNode('http_requests', 'basenode', '网络请求')
  node.setNodeFlag(VFNodeFlag.isTask).setSize(80, 80)

  node.addHandle(VFNodeConnectionType.inputs, 'input')
  node.addHandle(VFNodeConnectionType.outputs, 'output')

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
        { key: 'query', type: 'String', value: 'say' },
        { key: 'ask', type: 'String', value: 'hi' },
        { key: 'token', type: 'String', value: 'xxx' },
        { key: 'cooker', type: 'String', value: 'yyy' },
      ],
      uitype: 'vars_input',
    },
    'D_VARSINPUT',
  )
  node.addPayload(
    {
      label: '网络配置',
      type: 'HttpRequestConfig',
      key: 'request',
      data: {
        method: 'GET',
        url: 'https://api.example.com?{{query}}={{ask}}',
        headers: [{ key: 'Authorization', value: 'Bearer {{token}}' }],
        body: {
          type: 'none', // none|json|text|form_data|x_www_form_urlencoded
          content1: '', // json|text
          content2: [
            // { key: "", value: "" },
          ], // x-www-form-urlencoded
          content3: [
            // { key: "", type: "File", value: "" },// String|File
          ], // form-data
        },
        cookies: [{ key: 'cook', value: '{{cooker}}' }],
      },
      uitype: 'httprequests',
    },
    'D_CONFIG',
  )

  node.addPayload(
    {
      label: '超时配置',
      type: 'HttpTimeoutConfig',
      key: 'timeout',
      data: {
        connect: 3,
        read: 10,
        write: 5,
      },
      uitype: 'httptimeout',
    },
    'D_TIMEOUT',
  )

  node.addResultWithConnection(
    { label: '返回状态', type: 'String', key: 'status_code', data: '' },
    'output',
    'DR_STATUS',
  )
  node.addResultWithConnection(
    { label: '返回头', type: 'List', key: 'header', data: [] },
    'output',
    'DR_HEADER',
  )
  node.addResultWithConnection(
    { label: '返回状态', type: 'String', key: 'status_code', data: '' },
    'output',
    'DR_STATUS',
  )
  node.addResultWithConnection(
    { label: '返回Cookie', type: 'List', key: 'cookie', data: [] },
    'output',
    'DR_COOKIE',
  )
  node.addResultWithConnection(
    { label: '返回类型', type: 'String', key: 'content_type', data: [] },
    'output',
    'DR_CONTENTTYPE',
  )
  node.addResultWithConnection(
    { label: '返回结果', type: 'String', key: 'response', data: '' },
    'output',
    'DR_RESPONSE',
  )

  node.setOutputsUIType('tagoutputs')
  return node
}
