"use client"
import { createContext, useContext, useState, useEffect } from "react"

type Ctx = { pageTitle: string | null; setPageTitle: (t: string | null) => void }

const PageTitleContext = createContext<Ctx>({ pageTitle: null, setPageTitle: () => {} })

export function PageTitleProvider({ children }: { children: React.ReactNode }) {
  const [pageTitle, setPageTitle] = useState<string | null>(null)
  return (
    <PageTitleContext.Provider value={{ pageTitle, setPageTitle }}>
      {children}
    </PageTitleContext.Provider>
  )
}

export function usePageTitle(title: string | null | undefined) {
  const { setPageTitle } = useContext(PageTitleContext)
  useEffect(() => {
    if (title) setPageTitle(title)
    return () => setPageTitle(null)
  }, [title, setPageTitle])
}

export function usePageTitleValue() {
  return useContext(PageTitleContext).pageTitle
}
