'use client';

import { TimeTracker } from '../../components/dashboard/time-tracker';
import { StatsWidgets } from '../../components/dashboard/stats-widgets';

export default function DashboardPage() {
    return (
        <div className="flex flex-col items-center gap-12 max-w-4xl mx-auto w-full">
            <div className="flex flex-col items-center gap-4 text-center mb-8">
                <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-2">Good Morning, Employee</h2>
                <p className="text-zinc-500 text-lg max-w-md">Track your time with precision and analyze your productivity.</p>
            </div>

            <div className="w-full flex flex-col items-center gap-12">
                <TimeTracker />
                <StatsWidgets />
            </div>
        </div>
    )
}
