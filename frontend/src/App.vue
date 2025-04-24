<template>
  <n-config-provider :theme="darkTheme" :hljs="hljs" :locale="zhCN" :date-locale="dateZhCN">
    <n-dialog-provider>
      <n-message-provider>
        <div :style="{ height: '100vh', width: '100vw' }">
          <vflow />
        </div>
      </n-message-provider>
    </n-dialog-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import {
  NMessageProvider,
  darkTheme,
  NConfigProvider,
  NDialogProvider,
  dateZhCN,
  zhCN,
  NSpin,
  NFlex,
  NText,
} from 'naive-ui'
import vflow from './components/vflow.vue'
import hljs from 'highlight.js/lib/core'
import python_hljs from 'highlight.js/lib/languages/python'
import json_hljs from 'highlight.js/lib/languages/json'
import dajngo_hljs from 'highlight.js/lib/languages/django'
// import javascript_hljs from 'highlight.js/lib/languages/javascript'

hljs.registerLanguage('django', dajngo_hljs)
hljs.registerLanguage('json', json_hljs)
hljs.registerLanguage('python', python_hljs)
// hljs.registerLanguage('javascript', javascript_hljs)
</script>
