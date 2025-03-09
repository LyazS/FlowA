<template>
  <n-flex vertical>
    <n-flex vertical :style="{ width: '100%' }">
      <editable_header type="warning" :level="6"> 请求 Method & URL </editable_header>
      <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
        <n-select
          v-model:value="thisMethod"
          :options="HttpMethodSelect"
          :style="{ width: '8em' }"
          :disabled="!isEditorMode"
        />
        <n-input v-model:value="thisUrl" :style="{ flex: '1' }" :disabled="!isEditorMode" />
      </n-flex>
    </n-flex>
    <n-flex vertical :style="{ width: '100%' }">
      <n-flex class="flexctitem" justify="space-between">
        <editable_header type="warning" :level="6"> 请求头 Header </editable_header>
        <n-button text type="warning" @click="addHeader" :disabled="!isEditorMode">
          <template #icon>
            <n-icon>
              <Add />
            </n-icon>
          </template>
          新增Header
        </n-button>
      </n-flex>
      <template v-for="(item, index) in thisHeaders">
        <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
          <n-flex class="flexctitem" :style="{ width: '95%' }" :wrap="false">
            <n-auto-complete
              size="small"
              v-model:value="item.key"
              :options="HeaderKeySelectGroup"
              :disabled="!isEditorMode"
              placeholder="按'/'键自动填充"
              :get-show="headerKeyGetShow"
              :style="{ width: '50%' }"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
            <n-auto-complete
              size="small"
              v-model:value="item.value"
              placeholder="按'/'键自动填充"
              :disabled="!isEditorMode"
              :options="buildHeaderValueSelect(item.key)"
              :get-show="(value) => headerValueGetShow(item.key, value)"
              :style="{ width: '50%' }"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
          </n-flex>
          <n-button
            circle
            tertiary
            size="small"
            type="error"
            @click="rmHeader(index)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <Close />
              </n-icon>
            </template>
          </n-button>
        </n-flex>
      </template>
    </n-flex>
    <n-flex vertical :style="{ width: '100%' }">
      <n-flex class="flexctitem" justify="space-between">
        <editable_header type="warning" :level="6"> 请求体 Body </editable_header>
        <n-flex class="flexctitem" justify="flex-end">
          <n-button
            v-if="isBodyContentText"
            :disabled="!isEditorMode"
            text
            type="warning"
            @click="editBody_Json"
          >
            <template #icon>
              <n-icon>
                <CreateOutline />
              </n-icon>
            </template>
            放大编辑
          </n-button>
          <n-button
            v-else-if="isBodyContentXWWWForm || isBodyContentFormData"
            :disabled="!isEditorMode"
            text
            type="warning"
            @click="addBody_kv"
          >
            <template #icon>
              <n-icon>
                <Add />
              </n-icon>
            </template>
            添加
          </n-button>
          <n-select
            v-model:value="thisBody.type"
            :options="HttpBodyTypeSelect"
            :consistent-menu-width="false"
            :disabled="!isEditorMode"
            :style="{ width: 'auto' }"
          />
        </n-flex>
      </n-flex>
      <n-input
        v-if="isBodyContentText"
        v-model:value="thisBody.content1"
        type="textarea"
        size="small"
        :autosize="{
          minRows: 3,
          maxRows: 10,
        }"
        :disabled="!isEditorMode"
      />
      <template v-else-if="isBodyContentXWWWForm" v-for="(item, index) in thisBody.content2">
        <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
          <n-flex class="flexctitem" :style="{ width: '95%' }" :wrap="false">
            <n-input
              size="small"
              v-model:value="item.key"
              :style="{ width: '50%' }"
              placeholder="键"
              :disabled="!isEditorMode"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
            <n-input
              size="small"
              v-model:value="item.value"
              :style="{ width: '50%' }"
              placeholder="值"
              :disabled="!isEditorMode"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
          </n-flex>
          <n-button
            circle
            tertiary
            size="small"
            type="error"
            @click="rmBody_XWWWForm(index)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <Close />
              </n-icon>
            </template>
          </n-button>
        </n-flex>
      </template>
      <template v-else-if="isBodyContentFormData" v-for="(item, index) in thisBody.content3">
        <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
          <n-flex class="flexctitem" :style="{ width: '95%' }" :wrap="false">
            <n-input
              size="small"
              v-model:value="item.key"
              :style="{ width: '30%' }"
              placeholder="键"
              :disabled="!isEditorMode"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
            <n-select
              v-model:value="item.type"
              :options="FormDataContentTypeSelect"
              :disabled="!isEditorMode"
              :consistent-menu-width="false"
              :style="{ width: '20%' }"
            />
            <n-input
              v-if="item.type === 'String'"
              size="small"
              v-model:value="item.value"
              :disabled="!isEditorMode"
              :style="{ width: '50%' }"
              placeholder="值"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
            <cp_var_select
              v-else-if="item.type === 'file'"
              :style="{ width: '50%' }"
              size="small"
              :options="selfVarSelections"
              v-model:value="item.value"
            />
          </n-flex>
          <n-button
            circle
            tertiary
            size="small"
            type="error"
            @click="rmBody_FormData(index)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <Close />
              </n-icon>
            </template>
          </n-button>
        </n-flex>
      </template>
    </n-flex>
    <n-flex vertical :style="{ width: '100%' }">
      <n-flex class="flexctitem" justify="space-between">
        <editable_header type="warning" :level="6"> Cookies </editable_header>
        <n-button text type="warning" @click="addCookie" :disabled="!isEditorMode">
          <template #icon>
            <n-icon>
              <Add />
            </n-icon>
          </template>
          新增Cookie
        </n-button>
      </n-flex>
      <template v-for="(item, index) in thisCookies">
        <n-flex class="flexctitem" justify="space-between" :style="{ width: '100%' }" :wrap="false">
          <n-flex class="flexctitem" :style="{ width: '95%' }" :wrap="false">
            <n-input
              size="small"
              v-model:value="item.key"
              :style="{ width: '50%' }"
              placeholder="键"
              :disabled="!isEditorMode"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
            <n-input
              size="small"
              v-model:value="item.value"
              :style="{ width: '50%' }"
              placeholder="值"
              :disabled="!isEditorMode"
              @focus="isEditing = true"
              @blur="isEditing = false"
            />
          </n-flex>
          <n-button
            circle
            tertiary
            size="small"
            type="error"
            @click="rmCookie(index)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <Close />
              </n-icon>
            </template>
          </n-button>
        </n-flex>
      </template>
    </n-flex>
  </n-flex>
</template>

<script setup lang="ts">
import { ref, computed, h, inject, defineAsyncComponent } from 'vue'
import {
  NFlex,
  NText,
  NIcon,
  NButton,
  NInput,
  NSelect,
  NAutoComplete,
  type SelectOption,
  type AutoCompleteOption,
} from 'naive-ui'
import { Add, Close, CreateOutline } from '@vicons/ionicons5'
import editable_header from './common/header.vue'
import {
  isEditorMode,
  isEditing,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import {
  HeaderKeySelectGroup,
  HeaderValueSelect,
  HttpMethodSelect,
  HttpBodyTypeSelect,
  FormDataContentTypeSelect,
} from '@/schemas/http_schemas'
import type { Http_Header, Http_Body, Http_Cookie } from '@/schemas/http_schemas'
import type { CodeEditorLanguage } from '@/components/nodes/VFNodeInterface'

const cp_var_select = defineAsyncComponent(
  () => import('@/components/panelctrls/editables/common/var_select.vue'),
)

const props = defineProps<{
  selfVarSelections: SelectOption[]
  pid: string
}>()

// 获取节点数据
const { curSelectedNode } = useCurSelectedNode()

const createComputedConfig = <T,>(prop: string) => {
  return computed({
    get(): T {
      return curSelectedNode.value.data.payloads.byId[props.pid].data[prop]
    },
    set(value: T) {
      curSelectedNode.value.data.payloads.byId[props.pid].data[prop] = value
    },
  })
}

const thisMethod = createComputedConfig<string>('method')
const thisUrl = createComputedConfig<string>('url')

// 请求头
const thisHeaders = createComputedConfig<Http_Header[]>('headers')
const headerKeyGetShow = (value: string): boolean => {
  if (value.endsWith('/')) return true
  return false
}
const headerValueGetShow = (key: string, value: string): boolean => {
  if (value.endsWith('/') && HeaderValueSelect.hasOwnProperty(key)) return true
  return false
}
const buildHeaderValueSelect = (key: string): AutoCompleteOption[] => {
  if (HeaderValueSelect.hasOwnProperty(key)) {
    return HeaderValueSelect[key]
  }
  return []
}
const rmHeader = (index: number): void => {
  thisHeaders.value.splice(index, 1)
}
const addHeader = (): void => {
  thisHeaders.value.push({ key: '', value: '' })
}

// 请求体
const thisBody = createComputedConfig<Http_Body>('body')
const isBodyContentText = computed<boolean>(() => {
  if (thisBody.value.type === 'json') return true
  if (thisBody.value.type === 'plain-text') return true
  return false
})
const isBodyContentXWWWForm = computed<boolean>(() => {
  if (thisBody.value.type === 'x-www-form-urlencoded') return true
  return false
})
const isBodyContentFormData = computed<boolean>(() => {
  if (thisBody.value.type === 'form-data') return true
  return false
})
const codeLang = computed<CodeEditorLanguage>(() => {
  if (thisBody.value.type === 'json') {
    return 'json'
  } else if (thisBody.value.type === 'plain-text') {
    return 'text'
  }
  return 'text'
})
const editBody_Json = (): void => {
  CodeEditorPath.value = ['data', 'payloads', 'byId', props.pid, 'data', 'body', 'content1']
  CodeEditorLangType.value = codeLang.value
  isShowCodeEditor.value = true
}

const addBody_XWWWForm = (): void => {
  thisBody.value.content2.push({ key: '', value: '' })
}
const rmBody_XWWWForm = (index: number): void => {
  thisBody.value.content2.splice(index, 1)
}
const addBody_FormData = (): void => {
  thisBody.value.content3.push({ key: '', type: 'text', value: '' })
}
const rmBody_FormData = (index: number): void => {
  thisBody.value.content3.splice(index, 1)
}
const addBody_kv = (): void => {
  if (isBodyContentXWWWForm.value) {
    addBody_XWWWForm()
  } else {
    addBody_FormData()
  }
}

// 参数
const thisCookies = createComputedConfig<Http_Cookie[]>('cookies')
const rmCookie = (index: number): void => {
  thisCookies.value.splice(index, 1)
}
const addCookie = (): void => {
  thisCookies.value.push({ key: '', value: '' })
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
  flex-wrap: nowrap;
}
</style>
