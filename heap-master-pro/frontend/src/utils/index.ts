import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number, decimals: number = 2): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(decimals) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(decimals) + 'K'
  }
  return num.toFixed(decimals)
}

export function calculatePadMetrics(
  L: number,
  W: number,
  H: number,
  oreGrade: number,
  recovery: number,
  density: number = 1.7
) {
  const volume = L * W * H * 0.85 // Approximate with slope factor
  const tonnage = volume * density
  const recoverableCopper = tonnage * (oreGrade / 100) * (recovery / 100)
  
  return {
    volume_m3: Math.round(volume * 100) / 100,
    tonnage: Math.round(tonnage * 100) / 100,
    recoverable_copper_tonnes: Math.round(recoverableCopper * 100) / 100,
  }
}
