import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import type { Environment } from '@/types/environment'

interface EnvironmentContextType {
  currentEnv: Environment | null
  environments: Environment[]
  setCurrentEnv: (env: Environment | null) => void
  setEnvironments: (envs: Environment[]) => void
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined)

export function EnvironmentProvider({ children }: { children: ReactNode }) {
  const [currentEnv, setCurrentEnv] = useState<Environment | null>(null)
  const [environments, setEnvironments] = useState<Environment[]>([])

  return (
    <EnvironmentContext.Provider
      value={{
        currentEnv,
        environments,
        setCurrentEnv,
        setEnvironments,
      }}
    >
      {children}
    </EnvironmentContext.Provider>
  )
}

export function useEnvironment() {
  const context = useContext(EnvironmentContext)
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider')
  }
  return context
}
