<script setup lang="ts">
import { type Ref, ref, onMounted, reactive, h, inject, computed, watch } from 'vue'
import {
  useDialog,
  NText,
  NH3,
  NH4,
  NH5,
  NH6,
  NButton,
  NIcon,
  NButtonGroup,
  NScrollbar,
  NModal,
  NCard,
  NFlex,
  NGrid,
  NGridItem,
  NDivider,
  NDropdown,
  NEllipsis,
  NUpload,
  NSkeleton,
  useMessage,
  NInput,
  type UploadCustomRequestOptions,
} from 'naive-ui'
import {
  Ellipse,
  Close,
  Add,
  Pencil,
  DownloadOutline,
  CloudUploadOutline,
  CloudDownloadOutline,
  CaretDown,
  SaveOutline,
  EllipsisVertical,
  PushOutline,
} from '@vicons/ionicons5'
import {
  type WorkflowModeType,
  selectedNodeId,
  isEditorMode,
  isEditing,
  isShowCodeEditor,
  WorkflowID,
  WorkflowMode,
  WorkflowName,
  isShowVFlowMgr,
} from '@/hooks/useVFlowAttribute'
import { useVFlowRequest } from '@/services/useVFlowRequest'
import type { FAWorkflowInfo, FAReleaseWorkflowInfo } from '@/schemas/vflow_schemas'
import type { ButtonType } from '@/schemas/naiveui_schemas'
import { renderIcon, formatDateString, getErrorMessage } from '@/utils/tools'

const {
  setWFMode,
  checkWFStatusAndSwitch,
  clearWFStatus,

  createNewWorkflow,
  getWorkflows,
  switchWorkflow,
  renameWorkflow,
  uploadWorkflow,
  downloadWorkflow,
  deleteWorkflow,
  viewReleaseWorkflow,
  recordReleaseWorkflow,
  getReleaseWorkflows,
  downloadReleaseWorkflow,
  deleteReleaseWorkflow,
  editReleaseWorkflow,
  loadReleaseWorkflow,
} = useVFlowRequest()

const message = useMessage()
const dialog = useDialog()
const release_wfs = ref<FAReleaseWorkflowInfo[]>([])
const workflows = ref<(FAWorkflowInfo & { type: ButtonType })[]>([])

const updateWorkflowsAction = async () => {
  const items = await getWorkflows()
  if (items.type === 'success' && !!items.data) {
    workflows.value = []
    for (const item of items.data) {
      let wf_type: ButtonType = 'default'
      if (item.wid == WorkflowID.value) {
        wf_type = 'success'
      }
      workflows.value.push({
        ...item,
        type: wf_type,
      })
    }
  }
}

const updateReleaseWorkflowsAction = async () => {
  if (!WorkflowID.value) return
  const items = await getReleaseWorkflows(WorkflowID.value)
  if (items.type === 'success' && !!items.data) {
    release_wfs.value = items.data
  }
}

const createNewWorkflowAction = async () => {
  const new_name = ref('')
  dialog.warning({
    title: '新建工作流',
    content: () =>
      h(
        NInput,
        {
          value: new_name.value,
          onUpdateValue: (value) => {
            new_name.value = value.trimStart()
          },
          placeholder: '请输入工作流名称（1-20个字符）',
          autofocus: true,
          maxlength: 20,
          showCount: true,
          onFocus: () => {
            isEditing.value = true
          },
          onBlur: () => {
            isEditing.value = false
          },
        },
        {},
      ),
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      if (new_name.value.trim() === '') {
        message.error('名称不能为空')
        return
      }
      try {
        const finalName = new_name.value.trim()

        // 客户端验证
        if (!finalName) {
          message.error('名称不能为空')
          return
        }
        if (finalName.length < 1) {
          message.error('名称至少需要1个字符')
          return
        }

        // 执行创建
        const res = await createNewWorkflow(finalName)

        if (res.type === 'success') {
          message.success(`工作流【${finalName}】创建成功`)
          await updateWorkflowsAction() // 刷新列表
          isShowVFlowMgr.value = false
        } else {
          message.error(`创建失败: ${res.message}`)
        }
      } catch (error) {
        message.error(`创建失败: ${getErrorMessage(error)}`)
      } finally {
        isEditing.value = false
      }
    },
  })
}

const renameWorkflowAction = async (wid: string, originalName: string) => {
  const newName = ref(originalName.trim())

  // 创建响应式对话框
  dialog.info({
    title: '重命名工作流',
    content: () =>
      h(NInput, {
        value: newName.value,
        placeholder: '请输入新名称',
        autofocus: true,
        onFocus: () => {
          isEditing.value = true
        },
        onBlur: () => {
          isEditing.value = false
        },
        onUpdateValue: (val: string) => (newName.value = val),
        onKeydown: (e: KeyboardEvent) => e.stopPropagation(), // 防止冒泡
      }),
    positiveText: '确认',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const finalName = newName.value.trim()

        // 客户端校验
        if (!finalName) {
          message.error('名称不能为空')
          return
        }
        if (finalName === originalName) {
          message.warning('名称未修改')
          return
        }

        // 执行重命名
        const res = await renameWorkflow(wid, finalName)

        if (res.type === 'success') {
          message.success(`已重命名为【${finalName}】`)
          await updateWorkflowsAction() // 刷新列表
        } else {
          message.error('重命名失败，请检查网络')
        }
      } catch (error) {
        message.error(`重命名操作失败: ${getErrorMessage(error)}`)
      } finally {
        isEditing.value = false
      }
    },
    onNegativeClick: () => {
      isEditing.value = false
    },
  })
}

const downloadWorkflowAction = async (wid: string) => {
  const res = await downloadWorkflow(wid)
  if (res.type === 'success') {
    message.success(`工作流已下载`)
  } else {
    message.error(`下载失败: ${res.message}`)
  }
}

const deleteWorkflowAction = async (wid: string, wname: string) => {
  dialog.warning({
    title: '即将删除工作流',
    content: `【${wname}】`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await deleteWorkflow(wid, wname)
      if (res.type === 'success') {
        message.success(`工作流【${wname}】已删除`)
        await updateWorkflowsAction()
      } else {
        message.error(`删除失败: ${res.message}`)
      }
    },
  })
}

const wfOperations = [
  {
    label: '重命名',
    key: 'rename',
    icon: renderIcon(Pencil),
  },
  {
    label: '导出工作流',
    key: 'exportWF',
    icon: renderIcon(CloudDownloadOutline),
  },
  {
    label: '删除工作流',
    key: 'deleteWF',
    icon: renderIcon(Close),
  },
]
const handleSelectWFOperator = (key: string, wid: string, wname: string) => {
  if (key === 'rename') {
    renameWorkflowAction(wid, wname)
  } else if (key === 'exportWF') {
    downloadWorkflowAction(wid)
  } else if (key === 'deleteWF') {
    deleteWorkflowAction(wid, wname)
  }
}

const uploadWF = async ({
  file,
  data,
  headers,
  withCredentials,
  action,
  onFinish,
  onError,
  onProgress,
}: UploadCustomRequestOptions): Promise<void> => {
  if (file.file?.type === 'application/json') {
    const reader = new FileReader()

    reader.onload = async (event: ProgressEvent<FileReader>) => {
      try {
        if (!event.target?.result) {
          throw new Error('读取文件内容为空')
        }
        const jsonContent = JSON.parse(event.target.result as string)
        const res = await uploadWorkflow(file.name.replace('.json', ''), jsonContent)
        if (res.type === 'success') {
          message.success(`上传成功: ${file.name}`)
          isShowVFlowMgr.value = false
        } else {
          message.error(`上传失败: ${res.message}`)
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : '未知错误'
        message.error(`JSON 解析失败: ${errorMessage}`)
      }
    }

    reader.onerror = () => {
      const error = reader.error || new Error('文件读取失败')
      message.error(`读取文件失败: ${error}`)
    }

    reader.readAsText(file.file)
  } else {
    const error = new Error('不支持的文件类型')
    message.error(error.message)
  }
}

const switchWorkflowAction = async (wid: string) => {
  if (WorkflowID.value == wid) return
  const res = await switchWorkflow(wid)
  if (res.type === 'success') {
    message.success(`已切换工作流`)
    isShowVFlowMgr.value = false
  } else {
    message.error(`切换失败: ${res.message}`)
  }
}

const loadReleaseWorkflowAction = async (rwid: string, rname: string) => {
  const res = await loadReleaseWorkflow(WorkflowID.value, rwid)
  if (res.type === 'success') {
    isShowVFlowMgr.value = false
    message.success(`已加载版本【${rname}】`)
  } else {
    message.error(`版本加载失败: ${res.message}`)
  }
}

const viewReleaseWorkflowAction = async (rwid: string, rname: string) => {
  const res = await viewReleaseWorkflow(WorkflowID.value, rwid)
  if (res.type === 'success') {
    message.success(`查看版本【${rname}】`)
    isShowVFlowMgr.value = false
  } else {
    message.error(`查看失败: ${res.message}`)
  }
}

const recordReleaseWFAction = async () => {
  const record_name = ref('')
  const record_desc = ref('')
  dialog.warning({
    title: '记录当前版本工作流',
    content: () =>
      h(
        NFlex,
        {
          vertical: true,
          size: 'medium', // 可调整间距大小或使用[水平间距, 垂直间距]格式
        },
        {
          default: () => [
            h(NInput, {
              value: record_name.value,
              onUpdateValue: (value) => {
                record_name.value = value
              },
              placeholder: '版本名称',
              onFocus: () => {
                isEditing.value = true
              },
              onBlur: () => {
                isEditing.value = false
              },
            }),
            h(NInput, {
              type: 'textarea',
              autosize: { minRows: 3, maxRows: 5 },
              value: record_desc.value,
              onUpdateValue: (value) => {
                record_desc.value = value
              },
              placeholder: '版本描述',
              onFocus: () => {
                isEditing.value = true
              },
              onBlur: () => {
                isEditing.value = false
              },
            }),
          ],
        },
      ),
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const finalName = record_name.value.trim()

        // 客户端验证
        if (!finalName) {
          message.error('名称不能为空')
          return
        }
        if (finalName.length < 1 || finalName.length > 20) {
          message.error('版本名称需为1-20个字符')
          return
        }
        const res = await recordReleaseWorkflow(record_name.value, record_desc.value)
        if (res.type === 'success') {
          message.success(`版本【${finalName}】记录成功`)
          await updateReleaseWorkflowsAction()
        } else {
          message.error(`记录失败: ${res.message}`)
        }
      } catch (error) {
        message.error(`记录失败: ${getErrorMessage(error)}`)
      } finally {
        isEditing.value = false
      }
    },
  })
}

const rwfOperations = [
  {
    label: '加载',
    key: 'load',
    icon: renderIcon(PushOutline),
  },
  {
    label: '编辑',
    key: 'edit',
    icon: renderIcon(Pencil),
  },
  {
    label: '导出',
    key: 'export',
    icon: renderIcon(CloudDownloadOutline),
  },
  {
    label: '删除',
    key: 'delete',
    icon: renderIcon(Close),
  },
]

const editReleaseWorkflowAction = async (
  wid: string,
  rwid: string,
  originalName: string,
  originalDesc: string,
) => {
  const editState = reactive({
    name: originalName.trim(),
    desc: originalDesc.trim(),
    processing: false,
  })
  dialog.info({
    title: '编辑版本记录',
    content: () =>
      h(
        NFlex,
        {
          vertical: true,
          size: 'medium', // 可调整间距大小或使用[水平间距, 垂直间距]格式
        },
        {
          default: () => [
            h(NInput, {
              value: editState.name,
              onUpdateValue: (value) => {
                editState.name = value
              },
              placeholder: '版本名称',
              onFocus: () => {
                isEditing.value = true
              },
              onBlur: () => {
                isEditing.value = false
              },
            }),
            h(NInput, {
              type: 'textarea',
              autosize: { minRows: 3, maxRows: 5 },
              value: editState.desc,
              onUpdateValue: (value) => {
                editState.desc = value
              },
              placeholder: '版本描述',
              onFocus: () => {
                isEditing.value = true
              },
              onBlur: () => {
                isEditing.value = false
              },
            }),
          ],
        },
      ),
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      if (!WorkflowID.value) return
      try {
        // 客户端校验
        if (!editState.name.trim()) {
          message.error('版本名称不能为空')
          return
        }
        if (editState.name === originalName && editState.desc === originalDesc) {
          message.warning('内容未修改')
          return
        }

        // 执行修改
        const success = await editReleaseWorkflow(wid, rwid, editState.name, editState.desc)

        if (success) {
          message.success('版本信息编辑成功')
          await updateReleaseWorkflowsAction() // 刷新版本列表
        } else {
          message.error('版本信息编辑失败')
        }
      } catch (error) {
        message.error(`操作失败: ${getErrorMessage(error)}`)
      }
    },
  })
}

const deleteReleaseWorkflowAction = async (wid: string, rwid: string, rwname: string) => {
  dialog.warning({
    title: '即将删除版本记录',
    content: `【${rwname}】`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await deleteReleaseWorkflow(wid, rwid, rwname)
      if (res.type === 'success') {
        message.success(`版本【${rwname}】已删除`)
        await updateReleaseWorkflowsAction()
      } else {
        message.error(`删除失败: ${res.message}`)
      }
    },
  })
}

const downloadReleaseWorkflowAction = async (wid: string, rwid: string) => {
  const res = await downloadReleaseWorkflow(wid, rwid)
  if (res.type === 'success') {
    message.success(`版本下载成功`)
  } else {
    message.error(`下载失败: ${res.message}`)
  }
}

const handleSelectRWFOperator = (key: string, item: FAReleaseWorkflowInfo) => {
  if (!WorkflowID.value) return
  if (key === 'edit') {
    editReleaseWorkflowAction(WorkflowID.value, item.rwid, item.name, item.description)
  } else if (key === 'load') {
    loadReleaseWorkflowAction(item.rwid, item.name)
  } else if (key === 'export') {
    downloadReleaseWorkflowAction(WorkflowID.value, item.rwid)
  } else if (key === 'delete') {
    deleteReleaseWorkflowAction(WorkflowID.value, item.rwid, item.name)
  }
}

watch(isShowVFlowMgr, async (newVal) => {
  if (newVal) {
    await updateWorkflowsAction()
    await updateReleaseWorkflowsAction()
  }
})

onMounted(async () => {
  await updateWorkflowsAction()
  await updateReleaseWorkflowsAction()
})
</script>
<template>
  <n-modal v-model:show="isShowVFlowMgr" :close-on-esc="true" transform-origin="center">
    <n-card
      title="工作流管理器"
      closable
      @close="isShowVFlowMgr = false"
      :style="{ width: '80%', maxWidth: '1000px' }"
    >
      <n-grid x-gap="0" :cols="31">
        <n-grid-item :span="16">
          <n-flex vertical>
            <n-flex :style="{ flexWrap: 'nowrap', width: '100%' }">
              <n-button type="info" text @click="createNewWorkflowAction">
                <template #icon>
                  <n-icon>
                    <Add />
                  </n-icon>
                </template>
                新建工作流
              </n-button>
              <n-upload :show-file-list="false" :custom-request="uploadWF">
                <n-flex justify="center" align="center" :style="{ height: '100%' }">
                  <n-button type="info" text>
                    <template #icon>
                      <n-icon>
                        <CloudUploadOutline />
                      </n-icon>
                    </template>
                    导入工作流
                  </n-button>
                </n-flex>
              </n-upload>
            </n-flex>
            <n-scrollbar style="max-height: 50vh; padding-right: 5px">
              <n-flex vertical :style="{ width: '100%' }">
                <template v-for="(item, idx) in workflows" :key="'workflow_' + idx">
                  <n-flex
                    class="flexctitem"
                    :style="{ paddingRight: '12px' }"
                    :wrap="false"
                    :size="4"
                  >
                    <n-button
                      @click="switchWorkflowAction(item.wid)"
                      secondary
                      size="large"
                      :type="item.type"
                      :style="{ flex: '1' }"
                    >
                      <n-ellipsis style="max-width: 12em"> {{ item.name }}</n-ellipsis>
                    </n-button>
                    <n-dropdown
                      :options="wfOperations"
                      @select="(value) => handleSelectWFOperator(value, item.wid, item.name)"
                    >
                      <n-button size="large" text>
                        <template #icon>
                          <n-icon>
                            <EllipsisVertical />
                          </n-icon>
                        </template>
                      </n-button>
                    </n-dropdown>
                  </n-flex>
                </template>
              </n-flex>
            </n-scrollbar>
          </n-flex>
        </n-grid-item>
        <n-grid-item :span="1">
          <n-flex justify="center" align="center" :style="{ height: '100%' }">
            <n-divider vertical :style="{ height: '100%' }" />
          </n-flex>
        </n-grid-item>
        <n-grid-item :span="14">
          <template v-if="WorkflowID">
            <n-flex vertical>
              <n-flex
                justify="space-between"
                align="center"
                :style="{ height: '100%' }"
                :wrap="false"
              >
                <n-text>共 {{ release_wfs.length }} 个记录</n-text>
                <n-button type="info" text @click="recordReleaseWFAction">
                  <template #icon>
                    <n-icon>
                      <SaveOutline />
                    </n-icon>
                  </template>
                  记录当前版本
                </n-button>
              </n-flex>
              <n-scrollbar style="max-height: 50vh">
                <n-flex vertical :style="{ width: '100%' }">
                  <template v-for="(item, idx) in release_wfs" :key="'result_' + idx">
                    <n-flex
                      class="flexctitem"
                      :style="{ paddingRight: '12px' }"
                      :size="4"
                      :wrap="false"
                    >
                      <n-button
                        @click="viewReleaseWorkflowAction(item.rwid, item.name)"
                        tertiary
                        :style="{
                          display: 'block',
                          justifyContent: 'flex-start',
                          height: 'auto',
                          // width: '100%',
                          flex: '1',
                          padding: '6px',
                        }"
                      >
                        <n-flex vertical :style="{ width: '100%' }">
                          <n-text style="text-align: left" type="info">{{ item.name }} </n-text>
                          <n-ellipsis style="max-width: 240px; text-align: left">
                            {{ item.description }}
                            <template #tooltip>
                              <div style="text-align: left; max-width: 400px">
                                {{ item.description }}
                              </div>
                            </template>
                          </n-ellipsis>
                          <n-flex justify="space-between" align="center">
                            <n-text style="text-align: left" italic depth="3">
                              {{ formatDateString(item.releaseTime) }}
                            </n-text>
                          </n-flex>
                        </n-flex>
                      </n-button>
                      <n-dropdown
                        :options="rwfOperations"
                        @select="(value) => handleSelectRWFOperator(value, item)"
                        :style="{ padding: '0px' }"
                      >
                        <n-button size="large" text>
                          <template #icon>
                            <n-icon>
                              <EllipsisVertical />
                            </n-icon>
                          </template>
                        </n-button>
                      </n-dropdown>
                    </n-flex>
                  </template>
                </n-flex>
              </n-scrollbar>
            </n-flex>
          </template>
          <template v-else>
            <n-text>选择工作流以查看版本记录</n-text>
            <n-skeleton v-if="!WorkflowID" text :repeat="5" :sharp="false" size="medium" />
          </template>
        </n-grid-item>
      </n-grid>
    </n-card>
  </n-modal>
</template>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
