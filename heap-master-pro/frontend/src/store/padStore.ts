import { create } from 'zustand'
import type { HeapPad } from '@/types'

interface PadState {
  pads: HeapPad[]
  selectedPadId: number | null
  globalSlopeX: number
  globalSlopeY: number
  
  // Actions
  addPad: (pad: Omit<HeapPad, 'id' | 'created_at' | 'updated_at' | 'volume_m3' | 'tonnage' | 'recoverable_copper_tonnes'>) => void
  updatePad: (id: number, updates: Partial<HeapPad>) => void
  deletePad: (id: number) => void
  selectPad: (id: number | null) => void
  setGlobalSlope: (x: number, y: number) => void
  getSelectedPad: () => HeapPad | null
}

export const usePadStore = create<PadState>((set, get) => ({
  pads: [],
  selectedPadId: null,
  globalSlopeX: 0,
  globalSlopeY: 0,

  addPad: (padData) => {
    const newPad: HeapPad = {
      ...padData,
      id: Date.now(),
      volume_m3: 0,
      tonnage: 0,
      recoverable_copper_tonnes: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as HeapPad
    
    set((state) => ({
      pads: [...state.pads, newPad],
      selectedPadId: newPad.id,
    }))
  },

  updatePad: (id, updates) => {
    set((state) => ({
      pads: state.pads.map((pad) =>
        pad.id === id
          ? { ...pad, ...updates, updated_at: new Date().toISOString() }
          : pad
      ),
    }))
  },

  deletePad: (id) => {
    set((state) => ({
      pads: state.pads.filter((pad) => pad.id !== id),
      selectedPadId: state.selectedPadId === id ? null : state.selectedPadId,
    }))
  },

  selectPad: (id) => {
    set({ selectedPadId: id })
  },

  setGlobalSlope: (x, y) => {
    set({ globalSlopeX: x, globalSlopeY: y })
  },

  getSelectedPad: () => {
    const { pads, selectedPadId } = get()
    return pads.find((pad) => pad.id === selectedPadId) || null
  },
}))
