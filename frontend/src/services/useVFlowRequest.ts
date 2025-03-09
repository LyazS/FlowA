import { ref, watch, inject, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { type EventSourceMessage } from '@microsoft/fetch-event-source'
import { useVueFlow, type FlowExportObject } from '@vue-flow/core'
import { getUuid, setValueByPath, downloadJson, formatDateString } from '@/utils/tools'
import { postData, getData, type FAWorkflowOperationResponse } from '@/utils/requestMethod'
import { useVFlowManager } from '@/hooks/useVFlowManager'
import { useVFlowSaver } from '@/services/useVFlowSaver'
import { SubscribeSSE } from '@/utils/SSEMethod'
import { type NodeWithVFData } from '@/schemas/schemas'
import { useMessage } from 'naive-ui'
import { selectedNodeId } from '@/hooks/useVFlowAttribute'
import {
  WorkflowID,
  WorkflowName,
  AutoSaveMessage,
  Jinja2RenderNodeIDs,
  isEditorMode,
  WorkflowMode,
  WorkflowModeType,
} from '@/hooks/useVFlowAttribute'
import {
  FAProgressRequestType,
  type FANodeUpdateData,
  type SSEResponseData,
  type FAWorkflowInfo,
  type FAReleaseWorkflowInfo,
} from '@/schemas/vflow_schemas'

interface VFlowRequestInstance {
  setWFMode: (mode: WorkflowModeType) => void

  getWorkflows: () => Promise<FAWorkflowOperationResponse<FAWorkflowInfo[]>>
  createNewWorkflow: (name: string) => Promise<FAWorkflowOperationResponse>
  renameWorkflow: (wid: string, name: string) => Promise<FAWorkflowOperationResponse>
  uploadWorkflow: (
    name: string,
    wf_json: { version: string; vflow: FlowExportObject },
  ) => Promise<FAWorkflowOperationResponse>
  switchWorkflow: (wid: string | null) => Promise<FAWorkflowOperationResponse>
  downloadWorkflow: (wid: string | null) => Promise<FAWorkflowOperationResponse>
  deleteWorkflow: (wid: string | null, wname: string | null) => Promise<FAWorkflowOperationResponse>

  getReleaseWorkflows: (
    wid: string,
  ) => Promise<FAWorkflowOperationResponse<FAReleaseWorkflowInfo[]>>
  loadReleaseWorkflow: (
    wid: string | null,
    rwid: string | null,
  ) => Promise<FAWorkflowOperationResponse>
  viewReleaseWorkflow: (
    wid: string | null,
    rwid: string | null,
  ) => Promise<FAWorkflowOperationResponse>
  downloadReleaseWorkflow: (
    wid: string | null,
    rwid: string | null,
  ) => Promise<FAWorkflowOperationResponse>
  recordReleaseWorkflow: (
    name: string,
    description: string,
  ) => Promise<FAWorkflowOperationResponse<{ rwid: string; name: string }>>
  deleteReleaseWorkflow: (
    wid: string | null,
    rwid: string | null,
    rwname: string,
  ) => Promise<FAWorkflowOperationResponse>
  editReleaseWorkflow: (
    wid: string,
    rwid: string,
    name: string,
    description: string,
  ) => Promise<FAWorkflowOperationResponse>

  runflow: (runtype: 'full' | 'Incremental') => Promise<FAWorkflowOperationResponse>
  stopflow: () => Promise<FAWorkflowOperationResponse>
  clearWFStatus: () => Promise<void>
  checkWFStatusAndSwitch: () => Promise<void>
  onMountedFunc: () => Promise<void>
}
let instance: VFlowRequestInstance | null = null

export const useVFlowRequest = () => {
  if (instance) return instance

  const {
    findNode,
    getNodes,
    toObject,
    fromObject,
    removeNodes,
    nodesDraggable,
    nodesConnectable,
  } = useVueFlow()

  const { loadVflow } = useVFlowManager()
  const { autoSaveWorkflow } = useVFlowSaver()

  const message = useMessage()

  const updateNodeFromSSE = (data: SSEResponseData) => {
    const { nid, oriid, data: updatedatas } = data
    for (const udata of updatedatas) {
      const { data, path, type } = udata
      if (type === 'overwrite') {
        // 更新状态
        if (nid.includes('#') && path?.[0] === 'state' && path?.[1] === 'status') {
          const vf_node = findNode(oriid)
          if (vf_node && !(vf_node as NodeWithVFData).data.isAttachedNode()) {
            vf_node.data.state.copy[nid] = { status: data }
          }
        } else {
          // 更新其他数据
          const thenode = findNode(nid)
          if (thenode && !!path) {
            setValueByPath(thenode.data, path, data)
          }
        }
      } else if (type === 'append') {
      } else if (type === 'remove') {
      }
    }
  }

  const { subscribe, unsubscribe } = SubscribeSSE(
    async (response: Response) => {
      console.log('onopen SSE', response.ok)
    },
    (event: EventSourceMessage) => {
      console.log('[SSE] ', event.data)
      if (event.event === 'updatenode') {
        const data: SSEResponseData = JSON.parse(event.data)
        updateNodeFromSSE(data)
      } else if (event.event === 'batchupdatenode') {
        const datas: SSEResponseData[] = JSON.parse(event.data)
        for (const data of datas) {
          updateNodeFromSSE(data)
        }
      } else if (event.event === 'internalerror') {
        const data: string = JSON.parse(event.data)
        message.error(`内部错误: ${data}`)
      } else if (event.event === 'flowfinish') {
        unsubscribe()
        message.success('工作流运行完成')
      }
    },
    () => {
      console.log('onclose SSE')
    },
    (err: Error) => {
      console.log('onerror SSE', err)
    },
  )

  const setWFMode = (mode: WorkflowModeType) => {
    if (mode === WorkflowModeType.Edit) {
      nodesConnectable.value = true
      nodesDraggable.value = true
      WorkflowMode.value = WorkflowModeType.Edit
    } else if (mode === WorkflowModeType.View) {
      nodesConnectable.value = false
      nodesDraggable.value = false
      WorkflowMode.value = WorkflowModeType.View
    } else if (mode === WorkflowModeType.Run) {
      nodesConnectable.value = false
      nodesDraggable.value = false
      WorkflowMode.value = WorkflowModeType.Run
    }
  }

  const getWFIsRunning = async (wid: string | null): Promise<boolean> => {
    if (!wid) return false

    try {
      // 明确指定返回类型为boolean，自动处理接口错误
      const status = await getData<boolean>(`api/status?wid=${wid}`)
      console.debug(`[DEBUG] 工作流状态查询 ${wid}: `, status)
      return status
    } catch (error) {
      // 精准捕获错误类型
      const err = error as Error
      console.error(`[ERROR] 状态查询失败 [${wid}]`, err.message)
      message.error(`状态查询失败 [${wid}] ${err.message}`)
      // 根据业务需求返回安全值
      return false
    }
  }

  const clearWFStatus = async () => {
    selectedNodeId.value = null
    setWFMode(WorkflowModeType.Edit)
    unsubscribe()
  }

  const checkWFStatusAndSwitch = async () => {
    const isRunning = await getWFIsRunning(WorkflowID.value)
    if (isRunning) {
      setWFMode(WorkflowModeType.Run)
      subscribe(`${import.meta.env.VITE_API_URL}/api/progress`, 'POST', null, {
        type: FAProgressRequestType.VFlowUI,
        wid: WorkflowID.value,
        selected_nids: null,
      })
    }
  }

  const setWFIdAndName = (wid: string, name: string) => {
    WorkflowID.value = wid
    WorkflowName.value = name
    localStorage.setItem('curWorkflowID', wid)
  }

  const clearWFIdAndName = () => {
    WorkflowID.value = null
    WorkflowName.value = null
    localStorage.removeItem('curWorkflowID')
  }

  const renameWorkflow = async (
    wid: string,
    name: string,
  ): Promise<FAWorkflowOperationResponse> => {
    try {
      const data = {
        wid: wid,
        items: [
          {
            location: 'wfname',
            data: name.trim(),
          },
        ],
      }

      // 明确指定期望返回类型
      await postData<{ type: 'success' }>('workflow/update', data)

      // 统一状态更新逻辑
      if (WorkflowID.value === wid) {
        WorkflowName.value = name.trim()
      }
      return { type: 'success' }
    } catch (error) {
      // 处理未预期的错误
      const err = error as Error
      console.error(`[Workflow] 重命名失败 ${wid}:`, {
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const editReleaseWorkflow = async (
    wid: string,
    rwid: string,
    name: string,
    description: string,
  ): Promise<FAWorkflowOperationResponse> => {
    if (!wid || !rwid) {
      return { type: 'error', message: '无效的工作流或版本ID' }
    }
    try {
      const payload = {
        wid: wid,
        items: [
          { rwid, location: 'rwfname', data: name },
          { rwid, location: 'rwfdescription', data: description },
        ],
      }
      await postData('workflow/update', payload)
      return { type: 'success' }
    } catch (error) {
      // 处理未预期的错误
      const err = error as Error
      console.error('[Release] 请求异常', {
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const getWorkflows = async (): Promise<FAWorkflowOperationResponse<FAWorkflowInfo[]>> => {
    try {
      // 发送请求并指定响应类型
      const wfs = await getData<FAWorkflowInfo[]>('workflow/readall')

      // 记录成功日志
      console.debug('[Workflow] 获取列表成功', {
        count: wfs.length,
      })

      return { type: 'success', data: wfs }
    } catch (error) {
      // 处理未预期的错误
      const err = error as Error
      console.error('[Workflow] 请求异常', {
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const createNewWorkflow = async (name: string): Promise<FAWorkflowOperationResponse> => {
    try {
      // 类型安全的请求参数
      const payload = {
        type: 'new' as const,
        name: name.trim(),
      }

      // 明确响应类型并发送请求
      const wid = await postData<string>('workflow/create', payload)

      // 调试信息增强
      console.debug(`[Workflow] 创建成功 ID:${wid}`, { name })

      // 状态清理与设置
      clearWFStatus()
      removeNodes(getNodes.value)
      setWFIdAndName(wid, payload.name)

      return { type: 'success', data: wid }
    } catch (error) {
      // 精准错误处理
      const err = error as Error
      console.error(`[Workflow] 创建失败 [${name}]`, {
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const switchWorkflow = async (wid: string | null): Promise<FAWorkflowOperationResponse> => {
    // 参数校验阶段
    if (!wid) {
      console.warn('[Workflow] 非法工作流ID', wid)
      return {
        type: 'error',
        message: '无效的工作流wid',
      }
    }

    try {
      // 类型化请求参数
      const requestParams = {
        wid,
        locations: ['wfname', 'vflow'] as const,
      }
      const response = await postData<{
        wfname: string
        vflow: FlowExportObject
      }>('workflow/read', requestParams)
      clearWFStatus()
      loadVflow(response.vflow)
      setWFIdAndName(wid, response.wfname)
      checkWFStatusAndSwitch()

      // 记录成功日志
      console.debug('[Workflow] 切换成功', {
        wid,
        name: response.wfname,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Workflow] 切换失败', {
        wid,
        error: err.message,
        stack: err.stack,
      })

      // 清理无效状态
      clearWFStatus()

      return { type: 'error', message: err.message }
    }
  }

  const initWorkflow = async (wid: string | null): Promise<FAWorkflowOperationResponse> => {
    // 参数校验阶段
    if (!wid) {
      console.warn('[Workflow] 非法工作流ID', wid)
      return {
        type: 'error',
        message: '无效的工作流wid',
      }
    }

    try {
      // 类型化请求参数
      const requestParams = {
        wid,
        locations: ['wfname', 'vflow'] as const,
      }
      const response = await postData<{
        wfname: string
        vflow: FlowExportObject
      }>('workflow/read', requestParams)
      // clearWFStatus()
      loadVflow(response.vflow)
      setWFIdAndName(wid, response.wfname)
      checkWFStatusAndSwitch()

      // 记录成功日志
      console.debug('[Workflow] 切换成功', {
        wid,
        name: response.wfname,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Workflow] 切换失败', {
        wid,
        error: err.message,
        stack: err.stack,
      })

      // 清理无效状态
      clearWFStatus()

      return { type: 'error', message: err.message }
    }
  }

  const loadReleaseWorkflow = async (
    wid: string | null,
    rwid: string | null,
  ): Promise<FAWorkflowOperationResponse> => {
    try {
      // 参数有效性校验
      if (!wid || !rwid) {
        return { type: 'error', message: '无效的工作流或版本ID' }
      }

      // 类型明确的请求参数
      const params = {
        wid,
        rwid,
        locations: ['release'] as const,
      }
      const response = await postData<{ release: FlowExportObject }>('workflow/read', params)
      await clearWFStatus()
      loadVflow(response.release)
      autoSaveWorkflow()

      // 调试日志
      console.debug(`[Release] 已加载版本 ${rwid}`, response)
      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error(`[Release] 版本加载失败 [${rwid}]`, {
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const viewReleaseWorkflow = async (
    wid: string | null,
    rwid: string | null,
  ): Promise<FAWorkflowOperationResponse> => {
    // 参数校验
    if (!wid || !rwid) {
      console.warn('[Release] 无效的版本标识', { wid, rwid })
      return {
        type: 'error',
        message: '缺少有效的版本标识',
      }
    }

    try {
      // 类型化请求参数
      const params = {
        wid,
        rwid,
        locations: ['release'] as const,
      }
      const response = await postData<{ release: FlowExportObject }>('workflow/read', params)
      loadVflow(response.release)
      setWFMode(WorkflowModeType.View)
      // 记录成功日志
      console.debug('[Release] 版本加载成功', {
        wid,
        rwid,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Release] 版本加载失败', {
        wid,
        rwid,
        error: err.message,
        stack: err.stack,
      })

      // 清理无效状态
      clearWFStatus()

      return {
        type: 'error',
        message: err.message,
        data: { wid, rwid },
      }
    }
  }

  const getReleaseWorkflows = async (
    wid: string | null,
  ): Promise<FAWorkflowOperationResponse<FAReleaseWorkflowInfo[]>> => {
    try {
      // 参数有效性校验
      if (!wid) {
        console.warn('[Release] 无效的工作流标识', wid)
        return {
          type: 'error',
          message: '无效的工作流标识',
        }
      }

      // 发送类型化请求
      const response = await postData<{ allReleases: FAReleaseWorkflowInfo[] }>('workflow/read', {
        wid,
        locations: ['allReleases'],
      })

      // 数据转换保障
      const releases = response.allReleases.map((release) => ({
        rwid: release.rwid,
        name: release.name,
        description: release.description,
        releaseTime: formatDateString(release.releaseTime),
      })) as FAReleaseWorkflowInfo[]

      // 记录监控点
      console.debug('[Release] 版本列表获取成功', {
        wid,
        count: releases.length,
      })

      return { type: 'success', data: releases }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Release] 版本获取失败', {
        wid,
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const uploadWorkflow = async (
    name: string,
    wfJson: { version: string; vflow: FlowExportObject },
  ): Promise<FAWorkflowOperationResponse> => {
    // 参数校验阶段
    if (!name?.trim()) {
      return {
        type: 'error',
        message: '工作流名称不能为空',
      }
    }

    try {
      // 构造类型安全的请求负载
      const payload = { type: 'upload', name, vflow: wfJson.vflow }

      // 发送请求并指定响应类型
      const wid = await postData<string>('workflow/create', payload)

      clearWFIdAndName()
      await switchWorkflow(wid)
      console.debug('[Workflow] 上传成功', {
        name,
        wid: wid,
      })
      return { type: 'success' }
    } catch (error) {
      const err = error as Error
      console.error('[Workflow] 上传失败', {
        error: err.message,
        stack: err.stack,
      })

      return {
        type: 'error',
        message: err.message,
      }
    }
  }

  const recordReleaseWorkflow = async (
    name: string,
    description: string,
  ): Promise<FAWorkflowOperationResponse<{ rwid: string; name: string }>> => {
    // 参数校验前置
    if (!name.trim() || name.length > 20) {
      return {
        type: 'error',
        message: '版本名称需为1-20个字符',
      }
    }

    try {
      // 类型化请求结构
      const requestPayload = {
        type: 'release' as const,
        wid: WorkflowID.value,
        name: name.trim(),
        description: description,
        vflow: toObject(),
      }

      // 发送请求并指定返回类型
      const result = await postData<{ rwid: string }>('workflow/create', requestPayload)

      // 记录成功日志
      console.debug('[Release] 版本记录成功', {
        wid: requestPayload.wid,
        rwid: result.rwid,
        name: requestPayload.name,
      })

      return {
        type: 'success',
        data: {
          rwid: result.rwid,
          name: requestPayload.name,
        },
      }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Release] 版本记录失败', {
        wid: WorkflowID.value,
        error: err.message,
        stack: err.stack,
      })

      // 返回标准错误结构
      return {
        type: 'error',
        message: err.message,
      }
    }
  }

  const downloadWorkflow = async (wid: string | null): Promise<FAWorkflowOperationResponse> => {
    // 参数校验
    if (!wid) {
      console.warn('[Download] 无效的工作流标识符', wid)
      return {
        type: 'error',
        message: '无效的工作流标识符',
      }
    }

    try {
      // 类型化请求参数
      const requestParams = {
        wid,
        locations: ['wfname', 'vflow'] as const,
      }

      // 发送请求并指定响应类型
      const response = await postData<{
        wfname: string
        vflow: FlowExportObject
      }>('workflow/read', requestParams)

      // 构造下载数据
      const payload = {
        version: '0.0.1',
        vflow: response.vflow,
      }

      // 安全文件名处理
      const safeFilename =
        response.wfname
          .replace(/[\\/:*?"<>|~#%&{}\[\]]/g, '_')
          .substring(0, 50)
          .trim() || 'unnamed_workflow'

      // 执行下载
      downloadJson(JSON.stringify(payload), `${safeFilename}.json`)

      // 记录成功日志
      console.debug('[Download] 下载成功', {
        wid,
        name: response.wfname,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Download] 下载失败', {
        wid,
        error: err.message,
        stack: err.stack,
      })

      return {
        type: 'error',
        message: err.message,
      }
    }
  }

  const downloadReleaseWorkflow = async (
    wid: string | null,
    rwid: string | null,
  ): Promise<FAWorkflowOperationResponse> => {
    // 参数校验
    if (!wid || !rwid) {
      console.warn('[Download] 无效的工作流版本标识', { wid, rwid })
      return {
        type: 'error',
        message: '无效的工作流版本标识',
      }
    }

    try {
      // 类型化请求参数
      const requestParams = {
        wid,
        rwid,
        locations: ['wfname', 'rwfname', 'release'] as const,
      }

      // 发送请求并指定响应类型
      const response = await postData<{
        wfname: string
        rwfname: string
        release: FlowExportObject
      }>('workflow/read', requestParams)

      // 构造版本化数据包
      const payload = {
        version: '0.0.1',
        flowData: response.release,
      }

      // 安全文件名处理
      const safeWfname =
        response.wfname
          .replace(/[\\/:*?"<>|~#%&{}\[\]$^+=;]/g, '_')
          .substring(0, 50)
          .trim() || `${wid.substring(0, 8)}`
      const safeRWfname =
        response.rwfname
          .replace(/[\\/:*?"<>|~#%&{}\[\]$^+=;]/g, '_')
          .substring(0, 50)
          .trim() || `${rwid.substring(0, 8)}`

      // 执行下载操作
      downloadJson(JSON.stringify(payload), `${safeWfname}_${safeRWfname}.json`)

      // 记录成功日志
      console.debug('[Release] 版本下载成功', {
        wid,
        rwid,
        filename: `${safeWfname}_${safeRWfname}.json`,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Release] 版本下载失败', {
        wid,
        rwid,
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const runflow = async (runtype: 'full' | 'Incremental'): Promise<FAWorkflowOperationResponse> => {
    // 参数校验
    if (!WorkflowID.value) {
      console.warn('[Run] 无效的工作流ID', WorkflowID.value)
      return {
        type: 'error',
        message: '无效的工作流标识符',
        data: { invalidWid: WorkflowID.value },
      }
    }

    try {
      // 准备请求数据
      for (const node of getNodes.value) {
        node.data.resetState()
      }
      const requestPayload = {
        type: runtype,
        wid: WorkflowID.value,
        vflow: toObject(),
      }

      // 发送请求
      const response = await postData<{
        type: 'validation' | 'isrunning' | 'internalerror' | 'success'
        validation_errors?: { nid: string; errors: string[] }[]
      }>('api/run', requestPayload)

      // 处理不同响应类型
      switch (response.type) {
        case 'validation':
          console.error('[Run] 验证失败', response.validation_errors)
          if (response.validation_errors) {
            for (const error of response.validation_errors) {
              const node = findNode(error.nid) as NodeWithVFData
              if (node) {
                node.data.state.validation_errors = [...error.errors]
              }
            }
          }
          return { type: 'error', message: '工作流配置错误' }
        case 'isrunning':
          return { type: 'error', message: '工作流正在运行中' }
        case 'success':
          console.debug('[Run] 启动成功')
          setWFMode(WorkflowModeType.Run)
          setTimeout(() => {
            console.debug('[Run] 订阅信息')
            subscribe(`${import.meta.env.VITE_API_URL}/api/progress`, 'POST', null, {
              type: 'VFlowUI',
              wid: WorkflowID.value,
              selected_nids: null,
            })
          }, 1000)
          return { type: 'success' }
        default:
          console.error('[Run] 未知响应类型', response)
          return { type: 'error', message: '未知的服务器响应' }
      }
    } catch (error) {
      // 处理系统级错误
      const err = error as Error
      console.error('[Run] 运行请求异常', {
        wid: WorkflowID.value,
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: '运行请求失败，请检查网络连接' }
    }
  }

  const stopflow = async (): Promise<FAWorkflowOperationResponse> => {
    // 参数有效性校验
    const currentWid = WorkflowID.value
    if (!currentWid) {
      console.warn('[Workflow] 停止操作 - 无效的工作流ID', currentWid)
      return { type: 'error', message: '当前工作流不可用' }
    }

    try {
      // 类型化请求参数
      const requestPayload = { type: 'Stop', wid: currentWid }

      await postData('api/stop', requestPayload)
      await clearWFStatus()
      await switchWorkflow(WorkflowID.value)
      // 记录成功日志
      console.debug('[Workflow] 停止成功', { wid: currentWid })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Workflow] 停止失败', {
        wid: currentWid,
        error: err.message,
        stack: err.stack,
      })

      // 尝试清理残留状态
      await clearWFStatus()

      return { type: 'error', message: err.message }
    }
  }

  const deleteWorkflow = async (
    wid: string | null,
    wname: string | null,
  ): Promise<FAWorkflowOperationResponse> => {
    // 参数校验
    if (!wid) {
      console.warn('[Delete] 无效的工作流标识符', wid)
      return {
        type: 'error',
        message: '无效的工作流标识符',
      }
    }

    try {
      // 类型化请求参数
      const requestPayload = {
        wid: wid,
      }

      // 发送删除请求
      await postData('workflow/delete', requestPayload)
      if (WorkflowID.value === wid) {
        await clearWFStatus()
        clearWFIdAndName()
        removeNodes(getNodes.value)
      }
      // 记录成功日志
      console.debug('[Delete] 删除成功', {
        wid,
        name: wname,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Delete] 删除失败', {
        wid,
        error: err.message,
        stack: err.stack,
      })

      return { type: 'error', message: err.message }
    }
  }

  const deleteReleaseWorkflow = async (
    wid: string | null,
    rwid: string | null,
    rwname: string,
  ): Promise<FAWorkflowOperationResponse> => {
    if (!wid || !rwid) {
      console.warn('[Delete] 无效的版本ID', { wid, rwid })
      return {
        type: 'error',
        message: '无效的版本ID',
      }
    }

    try {
      // 类型化请求参数
      const requestPayload = { wid, rwid }
      await postData('workflow/delete', requestPayload)

      // 记录审计日志
      console.debug('[Delete] 版本删除成功', {
        wid,
        rwid,
        name: rwname,
      })

      return { type: 'success' }
    } catch (error) {
      // 错误处理
      const err = error as Error
      console.error('[Delete] 版本删除失败', {
        wid,
        rwid,
        error: err.message,
        stack: err.stack,
      })

      return {
        type: 'error',
        message: err.message,
      }
    }
  }

  const onMountedFunc = async () => {
    const ls_wid = localStorage.getItem('curWorkflowID') || null
    if (ls_wid) {
      Jinja2RenderNodeIDs.value =
        JSON.parse(localStorage.getItem(`${ls_wid}:Jinja2RenderNodeIDs`) || '[]') ?? []
    }
    await initWorkflow(ls_wid)
    console.log('loadWorkflow Done.')
  }

  onUnmounted(() => {
    unsubscribe()
  })

  instance = {
    setWFMode,

    getWorkflows,
    createNewWorkflow,
    renameWorkflow,
    uploadWorkflow,
    switchWorkflow,
    downloadWorkflow,
    deleteWorkflow,

    getReleaseWorkflows,
    loadReleaseWorkflow,
    viewReleaseWorkflow,
    downloadReleaseWorkflow,
    recordReleaseWorkflow,
    deleteReleaseWorkflow,
    editReleaseWorkflow,

    runflow,
    stopflow,
    clearWFStatus,
    checkWFStatusAndSwitch,
    onMountedFunc,
  }
  return instance
}
