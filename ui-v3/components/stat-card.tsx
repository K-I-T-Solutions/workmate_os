import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

const accentMap = {
  blue: { icon: "bg-primary/15 text-primary glow-aura", line: "stroke-primary" },
  orange: { icon: "bg-chart-2/15 text-chart-2", line: "stroke-chart-2" },
  green: { icon: "bg-chart-3/15 text-chart-3", line: "stroke-chart-3" },
  emerald: { icon: "bg-chart-4/15 text-chart-4", line: "stroke-chart-4" },
  violet: { icon: "bg-chart-5/15 text-chart-5", line: "stroke-chart-5" },
} as const

function Sparkline({ data, className }: { data: number[]; className?: string }) {
  const w = 100
  const h = 28
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  const points = data
    .map((d, i) => {
      const x = (i / (data.length - 1)) * w
      const y = h - ((d - min) / range) * h
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(" ")
  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      className="h-7 w-full"
      aria-hidden="true"
    >
      <polyline
        points={points}
        fill="none"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        className={cn("opacity-80", className)}
      />
    </svg>
  )
}

export function StatCard({
  label,
  value,
  subtitle,
  icon: Icon,
  accent,
  trend,
}: {
  label: string
  value: string
  subtitle: string
  icon: LucideIcon
  accent: keyof typeof accentMap
  trend: number[]
}) {
  const a = accentMap[accent]
  return (
    <div className="flex flex-col rounded-xl border border-border bg-card p-5">
      <div className="flex items-start justify-between">
        <span className="text-sm font-medium text-muted-foreground">{label}</span>
        <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", a.icon)}>
          <Icon className="h-[18px] w-[18px]" />
        </div>
      </div>
      <div className="mt-4">
        <p className="font-heading text-2xl font-bold tracking-tight text-foreground">{value}</p>
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      </div>
      <div className="mt-4">
        <Sparkline data={trend} className={a.line} />
      </div>
    </div>
  )
}
