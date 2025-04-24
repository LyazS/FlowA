import { debounce } from 'lodash'
import { postData, getData } from '@/utils/requestMethod'
import { useVueFlow, type FlowExportObject } from '@vue-flow/core'

import {
  WorkflowModeType,
  WorkflowID,
  WorkflowName,
  WorkflowMode,
  AutoSaveMessage,
  Jinja2RenderNodeIDs,
  isEditorMode,
} from '@/hooks/useVFlowAttribute'

interface VFlowSaverInstance {
  autoSaveWorkflow: () => void
}
let instance: VFlowSaverInstance | null = null

export const useVFlowSaver = () => {
  if (instance) return instance
  const { toObject } = useVueFlow()

  const debouncedAutoSaveWorkflow = debounce(async () => {
    if (!WorkflowID.value) return
    const data = {
      wid: WorkflowID.value,
      items: [{ location: 'vflow', data: toObject() }],
    }
    await postData('workflow/update', data)
    AutoSaveMessage.value = `自动保存 ${new Date().toLocaleTimeString()}`
  }, 500)

  const autoSaveWorkflow = () => {
    if (WorkflowMode.value == WorkflowModeType.View) return
    console.log('try to autoSaveWorkflow')
    debouncedAutoSaveWorkflow()
  }
  instance = {
    autoSaveWorkflow,
  }
  return instance
}
