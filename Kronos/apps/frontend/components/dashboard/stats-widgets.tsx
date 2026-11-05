'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/utils/supabase/client';
import { Calendar, Clock, TrendingUp } from 'lucide-react';

interface WeeklySummary {
    totalSeconds: number;
    entriesCount: number;
    startOfWeek: string;
}

interface Prediction {
    predictedTime: string;
}

function formatDuration(seconds: number) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
}

export function StatsWidgets() {
    const [summary, setSummary] = useState<WeeklySummary | null>(null);
    const [prediction, setPrediction] = useState<Prediction | null>(null);
    const supabase = createClient();

    useEffect(() => {
        const fetchData = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            const headers = { 'Authorization': `Bearer ${session.access_token}` };

            // Fetch Summary
            fetch('http://localhost:3000/time-entries/weekly-summary', { headers })
                .then(res => res.json())
                .then(data => setSummary(data))
                .catch(err => console.error("Summary fetch error", err));

            // Fetch Prediction
            fetch('http://localhost:3000/time-entries/predict-out', { headers })
                .then(res => res.json())
                .then(data => setPrediction(data))
                .catch(err => console.error("Prediction fetch error", err));
        };

        fetchData();
    }, [supabase.auth]);

    if (!summary || !prediction) return <div className="animate-pulse h-32 bg-zinc-800/50 rounded-xl" />;

    const predictedDate = new Date(prediction.predictedTime);
    const predictedTimeStr = predictedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 w-full max-w-4xl mt-8">
            {/* Weekly Summary Card */}
            <div className="group relative overflow-hidden rounded-3xl bg-zinc-900/50 p-6 shadow-2xl border border-zinc-800 hover:border-zinc-700 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10 flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-zinc-400">
                        <Calendar className="h-4 w-4" />
                        <span className="text-sm font-medium">This Week</span>
                    </div>
                    <div className="text-4xl font-bold text-white tracking-tight">
                        {formatDuration(summary.totalSeconds)}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">
                        From {summary.entriesCount} sessions
                    </div>
                </div>
            </div>

            {/* Smart Prediction Card */}
            <div className="group relative overflow-hidden rounded-3xl bg-zinc-900/50 p-6 shadow-2xl border border-zinc-800 hover:border-zinc-700 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10 flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-emerald-400">
                        <TrendingUp className="h-4 w-4" />
                        <span className="text-sm font-medium">Smart Forecast</span>
                    </div>
                    <div className="text-4xl font-bold text-white tracking-tight">
                        {predictedTimeStr}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">
                        Predicted clock-out time based on your history.
                    </div>
                </div>
            </div>

            {/* Quality/Happiness Metric (Mock for now, could be real later) */}
            <div className="group relative overflow-hidden rounded-3xl bg-zinc-900/50 p-6 shadow-2xl border border-zinc-800 hover:border-zinc-700 transition-all duration-300 lg:col-span-1 md:col-span-2">
                <div className="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-orange-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10 flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-rose-400">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm font-medium">Daily Goal</span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span className="text-4xl font-bold text-white tracking-tight">92%</span>
                        <span className="text-sm text-zinc-500 mb-1">completed</span>
                    </div>
                    <div className="w-full h-2 bg-zinc-800 rounded-full mt-2 overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-rose-500 to-orange-500 w-[92%]" />
                    </div>
                </div>
            </div>
        </div>
    );
}
