import { create } from 'zustand'

interface ContractStatistics {
  totalCount: number
  draftCount: number
  signingCount: number
  completedCount: number
}

interface ContractState {
  statistics: ContractStatistics | null
  setStatistics: (stats: ContractStatistics) => void
}

export const useContractStore = create<ContractState>((set) => ({
  statistics: null,
  setStatistics: (statistics) => set({ statistics }),
}))
