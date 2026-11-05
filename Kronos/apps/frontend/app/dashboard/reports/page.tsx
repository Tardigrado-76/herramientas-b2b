'use client';

import { createClient } from '@/utils/supabase/client';
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface DailyData {
    date: string;
    hours: number;
}

interface MonthlySummary {
    month: string;
    year: number;
    dailyData: DailyData[];
}

export default function ReportsPage() {
    const [summary, setSummary] = useState<MonthlySummary | null>(null);
    const [loading, setLoading] = useState(true);
    const supabase = createClient();

    useEffect(() => {
        const fetchReport = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            try {
                const res = await fetch('http://localhost:3000/time-entries/monthly-summary', {
                    headers: {
                        'Authorization': `Bearer ${session.access_token}`
                    }
                });
                if (res.ok) {
                    const data = await res.json();
                    setSummary(data);
                }
            } catch (error) {
                console.error("Failed to fetch reports", error);
            } finally {
                setLoading(false);
            }
        };

        fetchReport();
    }, [supabase]);

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent"></div>
            </div>
        );
    }

    if (!summary || summary.dailyData.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-10 text-center text-zinc-500">
                <p>No data available for this month.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-8 p-8 h-full">
            <header>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                    Work Report
                </h1>
                <p className="text-zinc-500 mt-2">
                    Summary for <span className="text-white font-medium capitalize">{summary.month} {summary.year}</span>
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 rounded-3xl bg-zinc-900/50 border border-white/5 backdrop-blur-xl">
                    <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">Total Hours</h3>
                    <p className="text-4xl font-bold text-white">
                        {summary.dailyData.reduce((acc, curr) => acc + curr.hours, 0).toFixed(1)} <span className="text-xl text-zinc-600">h</span>
                    </p>
                </div>
                <div className="p-6 rounded-3xl bg-zinc-900/50 border border-white/5 backdrop-blur-xl">
                    <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">Days Worked</h3>
                    <p className="text-4xl font-bold text-white">
                        {summary.dailyData.filter(d => d.hours > 0).length} <span className="text-xl text-zinc-600">days</span>
                    </p>
                </div>
                {/* Placeholder for future metric */}
                <div className="p-6 rounded-3xl bg-zinc-900/50 border border-white/5 backdrop-blur-xl opacity-50">
                    <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-2">Overtime</h3>
                    <p className="text-4xl font-bold text-white">--</p>
                </div>
            </div>

            <div className="flex-1 min-h-[400px] w-full p-6 rounded-3xl bg-zinc-900/50 border border-white/5 backdrop-blur-xl">
                <h3 className="text-lg font-medium text-white mb-6">Daily Activity</h3>
                <div className="h-[350px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={summary.dailyData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                            <XAxis
                                dataKey="date"
                                stroke="#71717a"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => new Date(value).getDate().toString()}
                            />
                            <YAxis
                                stroke="#71717a"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                unit="h"
                            />
                            <Tooltip
                                cursor={{ fill: '#ffffff05' }}
                                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '12px' }}
                                itemStyle={{ color: '#fff' }}
                            />
                            <Bar
                                dataKey="hours"
                                fill="#8b5cf6"
                                radius={[4, 4, 0, 0]}
                                barSize={40}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
