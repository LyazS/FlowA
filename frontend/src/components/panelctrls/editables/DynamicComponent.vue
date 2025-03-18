<template>
    <component
      v-if="componentData"
      :is="componentData.Type"
      v-bind="processedProps"
    >
      <template v-for="(slotContent, slotName) in componentData.Slots" :key="slotName" v-slot:[slotName]>
        <dynamic-component
          v-for="(childComponent, index) in slotContent"
          :key="`${slotName}-${index}`"
          :component-data="childComponent"
          :node-data="nodeData"
        />
      </template>
    </component>
  </template>
  
  <script setup lang="ts">
  import { computed, defineProps, type PropType } from 'vue';
  import { NInput, NText } from 'naive-ui'; // Import your UI components
  
  // Define types to match Python models
  enum PropVarType {
    Value = "Value",
    Ref = "Ref",
    VModel = "VModel"
  }
  
  interface PropVar {
    Type: PropVarType;
    Data: any;
  }
  
  interface ComponentData {
    Type: string;
    Props: Record<string, PropVar>;
    Slots?: Record<string, ComponentData[]>;
  }
  
  // Define props with TypeScript types
  const props = defineProps({
    componentData: {
      type: Object as PropType<ComponentData>,
      required: true
    },
    nodeData: {
      type: Object as PropType<Record<string, any>>,
      required: true
    }
  });
  
  // Keep a registry of available components
  const componentRegistry: Record<string, any> = {
    NInput,
    NText,
    // Add more components as needed
  };
  
  // Process props based on PropVarType
  const processedProps = computed(() => {
    const result: Record<string, any> = {};
    
    if (!props.componentData || !props.componentData.Props) {
      return result;
    }
    
    for (const [key, propVar] of Object.entries(props.componentData.Props)) {
      if (!propVar || !propVar.Type) continue;
      
      switch (propVar.Type) {
        case PropVarType.Value:
          // Direct value assignment
          result[key] = propVar.Data;
          break;
          
        case PropVarType.Ref:
          // Create computed property for ref
          result[key] = computed({
            get: () => getNestedValue(props.nodeData, propVar.Data),
            set: (value) => setNestedValue(props.nodeData, propVar.Data, value)
          });
          break;
          
        case PropVarType.VModel:
          // For v-model, create the value binding and corresponding update event
          const modelName = key === 'modelValue' ? 'update:modelValue' : `update:${key}`;
          result[key] = computed({
            get: () => getNestedValue(props.nodeData, propVar.Data),
            set: (value) => setNestedValue(props.nodeData, propVar.Data, value)
          });
          
          // Add update event handler
          result[modelName] = (newValue: any) => {
            setNestedValue(props.nodeData, propVar.Data, newValue);
          };
          break;
      }
    }
    
    return result;
  });
  
  // Helper function to get nested value from path array
  function getNestedValue(obj: Record<string, any>, path: string[]): any {
    if (!path || !Array.isArray(path) || path.length === 0) return undefined;
    
    let current = obj;
    for (const key of path) {
      if (current === null || current === undefined) return undefined;
      current = current[key];
    }
    
    return current;
  }
  
  // Helper function to set nested value from path array
  function setNestedValue(obj: Record<string, any>, path: string[], value: any): void {
    if (!path || !Array.isArray(path) || path.length === 0) return;
    
    let current = obj;
    for (let i = 0; i < path.length - 1; i++) {
      const key = path[i];
      if (current[key] === undefined) {
        current[key] = typeof path[i + 1] === 'number' ? [] : {};
      }
      current = current[key];
    }
    
    const lastKey = path[path.length - 1];
    current[lastKey] = value;
  }
  </script>
  
  <script lang="ts">
  // Component registration for global use
  export default {
    name: 'DynamicComponent'
  }
  </script>