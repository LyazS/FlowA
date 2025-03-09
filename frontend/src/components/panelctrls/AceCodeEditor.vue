<script setup lang="ts">
import { type Ref, ref, onMounted, onUnmounted, reactive, inject, computed } from 'vue'
import { useVueFlow } from '@vue-flow/core'
import { NText, NModal, NCard, NFlex } from 'naive-ui'
import { getValueByPath, setValueByPath, isPathConnected } from '../../utils/tools.js'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import {
  selectedNodeId,
  isEditorMode,
  isEditing,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'

// =======================================================================================
import { VAceEditor } from 'vue3-ace-editor'
import ace from 'ace-builds'
import modePythonUrl from 'ace-builds/src-noconflict/mode-python?url'
ace.config.setModuleUrl('ace/mode/python', modePythonUrl)
import modeJsonUrl from 'ace-builds/src-noconflict/mode-json?url'
ace.config.setModuleUrl('ace/mode/json', modeJsonUrl)
import modeMarkdownUrl from 'ace-builds/src-noconflict/mode-markdown?url'
ace.config.setModuleUrl('ace/mode/markdown', modeMarkdownUrl)
import modeTextUrl from 'ace-builds/src-noconflict/mode-text?url'
ace.config.setModuleUrl('ace/mode/text', modeTextUrl)
import modeDjangoUrl from 'ace-builds/src-noconflict/mode-django?url'
ace.config.setModuleUrl('ace/mode/django', modeDjangoUrl)
import themeUrl from 'ace-builds/src-noconflict/theme-tomorrow_night_bright?url'
ace.config.setModuleUrl('ace/theme/tomorrow_night_bright', themeUrl)

// import workerBaseUrl from "ace-builds/src-noconflict/worker-base?url";
// ace.config.setModuleUrl("ace/mode/base", workerBaseUrl);
import snippetsPyhontUrl from 'ace-builds/src-noconflict/snippets/python?url'
ace.config.setModuleUrl('ace/snippets/python', snippetsPyhontUrl)
import extSearchboxUrl from 'ace-builds/src-noconflict/ext-searchbox?url'
ace.config.setModuleUrl('ace/ext/searchbox', extSearchboxUrl)
import 'ace-builds/src-noconflict/ext-language_tools'
// ace.require('ace/ext/language_tools')// ts会报错说没有这个require方法，实际上可以不需要这行也能正确导入
import extAutocompleterUrl from 'ace-builds/src-noconflict/ext-language_tools?url'
ace.config.setModuleUrl('ace/ext/autocompleter', extAutocompleterUrl)
const enableAutocompletion = computed(() => {
  if (CodeEditorLangType.value === 'python') return true
  if (CodeEditorLangType.value === 'json') return true
  else return false
})
const options = reactive({
  // useWorker: true, // 启用语法检查,必须为true
  enableBasicAutocompletion: enableAutocompletion, // 自动补全
  enableLiveAutocompletion: enableAutocompletion, // 智能补全
  enableSnippets: enableAutocompletion, // 启用代码段
  showPrintMargin: false, // 去掉灰色的线，printMarginColumn
  highlightActiveLine: true, // 高亮行
  highlightSelectedWord: true, // 高亮选中的字符
  copyWithEmptySelection: true, // 复制时不选中任何内容则复制一整行
  tabSize: 4, // tab锁进字符
  fontSize: 14, // 设置字号
  cursorStyle: 'ace', // 光标样式
  wrap: false, // 是否换行
  readOnly: false, // 是否可编辑
  // minLines: 10, // 最小行数，minLines和maxLines同时设置之后，可以不用给editor再设置高度
  // maxLines: 50, // 最大行数
  customScrollbar: true, // 自定义滚动条
  vScrollBarAlwaysVisible: true, // 永远显示垂直滚动条
})
// =======================================================================================

const { curSelectedNode } = useCurSelectedNode()
const codelabel = computed(() => {
  if (!selectedNodeId.value) return ''
  return `${curSelectedNode.value.data.label}`
})
const codedata = computed({
  get() {
    if (!selectedNodeId.value) return ''
    return getValueByPath(curSelectedNode.value, CodeEditorPath.value)
  },
  set(value) {
    setValueByPath(curSelectedNode.value, CodeEditorPath.value, value)
  },
})

const isShow = computed(() => {
  return isPathConnected(curSelectedNode.value, CodeEditorPath.value) && isShowCodeEditor.value
})
</script>
<template>
  <n-modal :show="isShow" display-directive="if" :close-on-esc="false">
    <n-card
      :title="codelabel"
      closable
      @close="isShowCodeEditor = false"
      :style="{ width: '90%' }"
      content-style="padding: 10px"
    >
      <v-ace-editor
        v-model:value="codedata"
        :lang="CodeEditorLangType"
        theme="tomorrow_night_bright"
        :options="options"
        style="height: calc(100vh - 200px)"
        @blur="isEditing = false"
        @focus="isEditing = true"
      />
    </n-card>
  </n-modal>
</template>
