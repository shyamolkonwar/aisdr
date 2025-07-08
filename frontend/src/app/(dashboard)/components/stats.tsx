'use client'

interface Stat {
  name: string
  value: number | string
}

interface DashboardStatsProps {
  stats: Stat[]
}

export default function DashboardStats({ stats }: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.name} className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">{stat.name}</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
            {stat.value}
          </dd>
        </div>
      ))}
    </div>
  )
}