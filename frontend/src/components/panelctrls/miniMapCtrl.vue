<script setup lang="ts">
import { Controls, ControlButton } from '@vue-flow/controls'
import { Icon } from '@vicons/utils'
import { Add, Remove, Scan, LockOpenOutline, LockClosed } from '@vicons/ionicons5'
</script>

<template>
  <Controls
    class="vue-flow__controls-minimapctrl"
    position="bottom-left"
    :style="{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }"
  >
    <template #icon-zoom-in>
      <Icon class="ctrl-icon">
        <Add />
      </Icon>
    </template>
    <template #icon-zoom-out>
      <Icon class="ctrl-icon">
        <Remove />
      </Icon>
    </template>
    <template #icon-fit-view>
      <Icon class="ctrl-icon">
        <Scan />
      </Icon>
    </template>
    <template #icon-unlock>
      <Icon class="ctrl-icon">
        <LockOpenOutline />
      </Icon>
    </template>
    <template #icon-lock>
      <Icon class="ctrl-icon">
        <LockClosed />
      </Icon>
    </template>
  </Controls>
</template>

<style>
.vue-flow__controls-minimapctrl {
  transform: scale(120%) translateX(5px);
}

.vue-flow__controls-minimapctrl .vue-flow__controls-button {
  border-radius: 2px;
  border: 2px solid rgb(52, 52, 56);
  background: rgb(52, 52, 56);
}

.vue-flow__controls-minimapctrl .vue-flow__controls-button:hover {
  border: 2px solid rgb(102, 102, 106);
  background: rgb(102, 102, 106);
}

.vue-flow__controls-minimapctrl .vue-flow__controls-button:disabled {
  border: 2px solid rgb(52, 52, 56);
  background: rgb(52, 52, 56);
}

.vue-flow__controls-minimapctrl .vue-flow__controls-button:disabled svg {
  color: black;
}
</style>

<style scoped>
.ctrl-icon {
  color: rgb(226, 226, 226);
  transform: scale(1.7);
}
</style>
