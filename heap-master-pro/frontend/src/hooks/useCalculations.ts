import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { calculationsApi } from '@/services/api'
import type {
  RecoveryInput,
  OPEXInput,
  PLSInput,
  ScheduleInput,
  PadVolumeInput,
  AcidOptimizationInput,
} from '@/types'

export function useRecoveryCalculation() {
  return useMutation({
    mutationFn: (data: RecoveryInput) => calculationsApi.calculateRecovery(data),
  })
}

export function useOPEXCalculation() {
  return useMutation({
    mutationFn: (data: OPEXInput) => calculationsApi.calculateOPEX(data),
  })
}

export function usePLSCalculation() {
  return useMutation({
    mutationFn: (data: PLSInput) => calculationsApi.calculatePLS(data),
  })
}

export function useScheduleCalculation() {
  return useMutation({
    mutationFn: (data: ScheduleInput) => calculationsApi.calculateSchedule(data),
  })
}

export function useVolumeCalculation() {
  return useMutation({
    mutationFn: (data: PadVolumeInput) => calculationsApi.calculateVolume(data),
  })
}

export function useAcidOptimization() {
  return useMutation({
    mutationFn: (data: AcidOptimizationInput) => calculationsApi.optimizeAcid(data),
  })
}
