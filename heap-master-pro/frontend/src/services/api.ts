import axios from 'axios'
import type {
  RecoveryInput,
  RecoveryOutput,
  OPEXInput,
  OPEXOutput,
  PLSInput,
  PLSOutput,
  ScheduleInput,
  ScheduleOutput,
  PadVolumeInput,
  PadVolumeOutput,
  AcidOptimizationInput,
  AcidOptimizationOutput,
} from '@/types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const calculationsApi = {
  async calculateRecovery(data: RecoveryInput): Promise<RecoveryOutput> {
    const response = await api.post<RecoveryOutput>('/calculate/recovery', data)
    return response.data
  },

  async calculateOPEX(data: OPEXInput): Promise<OPEXOutput> {
    const response = await api.post<OPEXOutput>('/calculate/opex', data)
    return response.data
  },

  async calculatePLS(data: PLSInput): Promise<PLSOutput> {
    const response = await api.post<PLSOutput>('/calculate/pls', data)
    return response.data
  },

  async calculateSchedule(data: ScheduleInput): Promise<ScheduleOutput> {
    const response = await api.post<ScheduleOutput>('/calculate/schedule', data)
    return response.data
  },

  async calculateVolume(data: PadVolumeInput): Promise<PadVolumeOutput> {
    const response = await api.post<PadVolumeOutput>('/calculate/volume', data)
    return response.data
  },

  async optimizeAcid(data: AcidOptimizationInput): Promise<AcidOptimizationOutput> {
    const response = await api.post<AcidOptimizationOutput>('/calculate/acid-optimize', data)
    return response.data
  },

  async calculateMultiple(data: Record<string, any>): Promise<any> {
    const response = await api.post('/calculate', data)
    return response.data
  },
}

export default api
