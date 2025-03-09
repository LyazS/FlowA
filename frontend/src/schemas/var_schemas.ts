import type { AllVariableTypes } from '@/schemas/select_schemas'

export interface VariableItem {
  key: string
  type: AllVariableTypes
  value: string
}
