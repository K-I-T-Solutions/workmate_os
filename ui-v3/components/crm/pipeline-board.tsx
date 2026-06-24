"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { crmService } from "@/lib/crm/service"
import type { Customer, PipelineStage } from "@/lib/crm/types"
import { BuildingIcon, MailIcon, PhoneIcon, ExternalLinkIcon } from "lucide-react"

const STAGES: { id: PipelineStage; label: string; color: string; headerColor: string }[] = [
  { id: "new_lead",    label: "Neuer Lead",    color: "border-slate-200 dark:border-slate-700",   headerColor: "bg-slate-100 dark:bg-slate-800" },
  { id: "qualified",  label: "Qualifiziert",  color: "border-blue-200 dark:border-blue-800",    headerColor: "bg-blue-50 dark:bg-blue-950" },
  { id: "proposal",   label: "Angebot",       color: "border-violet-200 dark:border-violet-800", headerColor: "bg-violet-50 dark:bg-violet-950" },
  { id: "negotiation",label: "Verhandlung",   color: "border-amber-200 dark:border-amber-800",  headerColor: "bg-amber-50 dark:bg-amber-950" },
  { id: "won",        label: "Gewonnen",      color: "border-green-200 dark:border-green-800",  headerColor: "bg-green-50 dark:bg-green-950" },
  { id: "lost",       label: "Verloren",      color: "border-red-200 dark:border-red-800",      headerColor: "bg-red-50 dark:bg-red-950" },
]

const TYPE_ICON: Record<string, string> = {
  business: "🏢", individual: "👤", creator: "✨", government: "🏛️",
}

function CustomerCard({
  customer,
  onDragStart,
}: {
  customer: Customer
  onDragStart: (e: React.DragEvent, id: string) => void
}) {
  const router = useRouter()
  return (
    <div
      draggable
      onDragStart={e => onDragStart(e, customer.id)}
      onClick={() => router.push(`/crm/customers/${customer.id}`)}
      className="group cursor-grab active:cursor-grabbing rounded-lg border bg-card p-3 shadow-sm hover:shadow-md hover:border-primary/40 transition-all select-none"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-base shrink-0">{TYPE_ICON[customer.type ?? ""] ?? "🏢"}</span>
          <p className="font-medium text-sm truncate">{customer.name}</p>
        </div>
        <button
          onClick={e => { e.stopPropagation(); router.push(`/crm/customers/${customer.id}`) }}
          className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground shrink-0"
        >
          <ExternalLinkIcon className="h-3.5 w-3.5" />
        </button>
      </div>

      {customer.customer_number && (
        <p className="mt-1 text-xs font-mono text-muted-foreground">{customer.customer_number}</p>
      )}

      <div className="mt-2 space-y-1">
        {customer.email && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MailIcon className="h-3 w-3 shrink-0" />
            <span className="truncate">{customer.email}</span>
          </div>
        )}
        {customer.phone && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <PhoneIcon className="h-3 w-3 shrink-0" />
            <span>{customer.phone}</span>
          </div>
        )}
        {customer.city && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <BuildingIcon className="h-3 w-3 shrink-0" />
            <span>{customer.city}{customer.country ? `, ${customer.country}` : ""}</span>
          </div>
        )}
      </div>
    </div>
  )
}

function KanbanColumn({
  stage,
  customers,
  onDragStart,
  onDrop,
}: {
  stage: typeof STAGES[number]
  customers: Customer[]
  onDragStart: (e: React.DragEvent, id: string) => void
  onDrop: (stageId: PipelineStage) => void
}) {
  const [dragOver, setDragOver] = useState(false)

  return (
    <div
      className={`flex flex-col rounded-xl border-2 transition-colors min-w-[260px] w-[260px] shrink-0 h-full ${stage.color} ${dragOver ? "border-primary bg-primary/5" : ""}`}
      onDragOver={e => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={e => { e.preventDefault(); setDragOver(false); onDrop(stage.id) }}
    >
      {/* Column header */}
      <div className={`flex items-center justify-between rounded-t-[10px] px-3 py-2.5 ${stage.headerColor}`}>
        <span className="text-sm font-semibold">{stage.label}</span>
        <span className="rounded-full bg-background/60 px-2 py-0.5 text-xs font-medium tabular-nums">
          {customers.length}
        </span>
      </div>

      {/* Cards */}
      <div className="flex flex-col gap-2 p-2 flex-1 min-h-0 overflow-y-auto">
        {customers.map(c => (
          <CustomerCard key={c.id} customer={c} onDragStart={onDragStart} />
        ))}
        {dragOver && customers.length === 0 && (
          <div className="rounded-lg border-2 border-dashed border-primary/40 h-20 flex items-center justify-center text-xs text-primary/60">
            Hier ablegen
          </div>
        )}
      </div>
    </div>
  )
}

export function PipelineBoard() {
  const [pipeline, setPipeline] = useState<Record<string, Customer[]>>({})
  const [loading, setLoading] = useState(true)
  const dragIdRef = useRef<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      const data = await crmService.getPipeline()
      setPipeline(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  function handleDragStart(e: React.DragEvent, id: string) {
    dragIdRef.current = id
    e.dataTransfer.effectAllowed = "move"
  }

  async function handleDrop(targetStage: PipelineStage) {
    const id = dragIdRef.current
    if (!id) return
    dragIdRef.current = null

    // Find current stage
    const currentStage = Object.entries(pipeline).find(([, customers]) =>
      customers.some(c => c.id === id)
    )?.[0]
    if (!currentStage || currentStage === targetStage) return

    // Optimistic update
    setPipeline(prev => {
      const next = { ...prev }
      const customer = prev[currentStage]?.find(c => c.id === id)
      if (!customer) return prev
      next[currentStage] = (prev[currentStage] ?? []).filter(c => c.id !== id)
      next[targetStage] = [{ ...customer, pipeline_stage: targetStage }, ...(prev[targetStage] ?? [])]
      return next
    })

    try {
      await crmService.updatePipelineStage(id, targetStage)
    } catch {
      // Rollback on error
      load()
    }
  }

  const totalLeads = Object.values(pipeline).reduce((s, c) => s + c.length, 0)

  return (
    <div className="flex flex-col gap-4 px-8 py-6 h-full">
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-semibold">Pipeline</h1>
          {!loading && (
            <p className="text-sm text-muted-foreground mt-0.5">{totalLeads} Kontakte in der Pipeline</p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
          Laden…
        </div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-4 flex-1 min-h-0">
          {STAGES.map(stage => (
            <KanbanColumn
              key={stage.id}
              stage={stage}
              customers={pipeline[stage.id] ?? []}
              onDragStart={handleDragStart}
              onDrop={handleDrop}
            />
          ))}
        </div>
      )}
    </div>
  )
}
