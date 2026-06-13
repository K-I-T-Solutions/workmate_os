"use client"

import { useEffect, useState, useCallback } from "react"
import { adminService } from "@/lib/admin/service"
import type { AuditLog } from "@/lib/admin/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react"

function fmtDateTime(d: string) {
  return new Date(d).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })
}

function DiffView({ oldVals, newVals }: { oldVals: Record<string, unknown> | null; newVals: Record<string, unknown> | null }) {
  const keys = new Set([...Object.keys(oldVals ?? {}), ...Object.keys(newVals ?? {})])
  if (keys.size === 0) return null
  return (
    <table className="w-full text-xs">
      <thead>
        <tr className="text-muted-foreground">
          <th className="text-left pb-1 font-medium w-32">Feld</th>
          <th className="text-left pb-1 font-medium">Vorher</th>
          <th className="text-left pb-1 font-medium">Nachher</th>
        </tr>
      </thead>
      <tbody>
        {[...keys].map(k => (
          <tr key={k} className="border-t">
            <td className="py-1 font-mono text-muted-foreground pr-3">{k}</td>
            <td className="py-1 text-red-600 dark:text-red-400 font-mono break-all pr-3">
              {oldVals?.[k] != null ? String(oldVals[k]) : "–"}
            </td>
            <td className="py-1 text-green-600 dark:text-green-400 font-mono break-all">
              {newVals?.[k] != null ? String(newVals[k]) : "–"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function AuditRow({ log }: { log: AuditLog }) {
  const [expanded, setExpanded] = useState(false)
  const hasDiff = log.old_values || log.new_values

  return (
    <div className="border-b last:border-0">
      <div className="flex items-center gap-3 px-4 py-3 hover:bg-muted/30 transition-colors">
        <div className="flex-1 min-w-0 grid grid-cols-[1fr_auto] gap-x-4 items-center">
          <div className="flex items-center gap-2 min-w-0">
            <span className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono font-medium shrink-0">{log.action}</span>
            <span className="text-sm truncate">
              <span className="font-medium">{log.entity_type}</span>
              {log.entity_id && <span className="text-muted-foreground ml-1 font-mono text-xs">{log.entity_id.slice(0, 8)}…</span>}
            </span>
          </div>
          <div className="flex items-center gap-3 shrink-0 text-xs text-muted-foreground">
            {log.ip_address && <span>{log.ip_address}</span>}
            <span>{fmtDateTime(log.timestamp)}</span>
            {hasDiff && (
              <button onClick={() => setExpanded(v => !v)} className="hover:text-foreground">
                {expanded ? <ChevronUpIcon className="h-3.5 w-3.5" /> : <ChevronDownIcon className="h-3.5 w-3.5" />}
              </button>
            )}
          </div>
        </div>
      </div>
      {expanded && hasDiff && (
        <div className="px-4 pb-3">
          <DiffView oldVals={log.old_values} newVals={log.new_values} />
        </div>
      )}
    </div>
  )
}

const PAGE_SIZE = 50

export function AuditTab() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [filterAction, setFilterAction] = useState("")
  const [filterEntity, setFilterEntity] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: Parameters<typeof adminService.listAuditLogs>[0] = {
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      }
      if (filterAction.trim()) params.action = filterAction.trim()
      if (filterEntity.trim()) params.entity_type = filterEntity.trim()
      const result = await adminService.listAuditLogs(params)
      setLogs(result.items)
      setTotal(result.total)
    } finally {
      setLoading(false)
    }
  }, [page, filterAction, filterEntity])

  useEffect(() => { load() }, [load])

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <Input
          value={filterAction}
          onChange={e => { setFilterAction(e.target.value); setPage(0) }}
          placeholder="Aktion filtern (create, update…)"
          className="w-52"
        />
        <Input
          value={filterEntity}
          onChange={e => { setFilterEntity(e.target.value); setPage(0) }}
          placeholder="Entitätstyp filtern"
          className="w-52"
        />
        <span className="ml-auto self-center text-sm text-muted-foreground">{total} Einträge</span>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : logs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Einträge gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          {logs.map(log => <AuditRow key={log.id} log={log} />)}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <Button variant="outline" size="sm" onClick={() => setPage(p => p - 1)} disabled={page === 0}>
            Zurück
          </Button>
          <span className="text-sm text-muted-foreground">Seite {page + 1} / {totalPages}</span>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1}>
            Weiter
          </Button>
        </div>
      )}
    </div>
  )
}
