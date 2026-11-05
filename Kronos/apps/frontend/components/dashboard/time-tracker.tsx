'use client';

import { useTimeTracker } from './use-time-tracker';
import { Button } from '@/components/ui/button';
import { Play, Pause, StopCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

function formatTime(seconds: number) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export function TimeTracker() {
    const { status, elapsedTime, isOnline, clockIn, clockOut, togglePause } = useTimeTracker();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return null; // Avoid hydration mismatch by rendering nothing on server initially for this dynamic component
    }

    if (status === 'LOADING') {
        return <div className="text-zinc-500">Loading timer...</div>;
    }

    const isWorking = status === 'IN';
    const isPaused = status === 'PAUSE_IN';

    return (
        <div className="relative group w-full max-w-sm">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-20 blur-3xl group-hover:opacity-30 transition-opacity duration-700"></div>

            <div className="relative flex flex-col items-center justify-center space-y-8 rounded-[2.5rem] border border-white/10 bg-zinc-900/40 p-10 backdrop-blur-2xl shadow-2xl">

                {/* Status Indicator */}
                <div className="flex flex-col items-center gap-2">
                    <div className={`
                        px-4 py-1.5 rounded-full border text-[10px] font-bold uppercase tracking-[0.2em] transition-colors
                        ${isWorking ? 'border-green-500/30 bg-green-500/10 text-green-400 shadow-[0_0_20px_-5px_rgba(74,222,128,0.5)]' :
                            isPaused ? 'border-amber-500/30 bg-amber-500/10 text-amber-400' :
                                'border-zinc-700 bg-zinc-800/50 text-zinc-500'}
                    `}>
                        {isWorking ? 'Tracking Time' : isPaused ? 'Timer Paused' : 'Ready to Start'}
                    </div>

                    {!isOnline && (
                        <div className="px-3 py-1 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400 text-[9px] font-bold uppercase tracking-wider animate-pulse">
                            Modo Offline Activo
                        </div>
                    )}
                </div>

                {/* Digital Clock Display */}
                <div className="flex flex-col items-center">
                    <div className="font-mono text-7xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-lg tabular-nums">
                        {formatTime(elapsedTime)}
                    </div>
                </div>

                {/* Controls */}
                <div className="flex items-center gap-6">
                    {status === 'OUT' ? (
                        <Button
                            size="icon"
                            className="h-20 w-20 rounded-full bg-gradient-to-tr from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 shadow-[0_10px_40px_-10px_rgba(16,185,129,0.5)] transition-all hover:scale-105 active:scale-95 border-0 ring-4 ring-green-500/10"
                            onClick={clockIn}
                        >
                            <Play className="h-8 w-8 text-white fill-white ml-1" />
                        </Button>
                    ) : (
                        <>
                            <Button
                                size="icon"
                                variant="outline"
                                className={`h-16 w-16 rounded-full border-2 transition-all hover:scale-105 active:scale-95 text-white/80 hover:text-white backdrop-blur-md
                                    ${isPaused ?
                                        'border-emerald-500/50 bg-emerald-500/10 hover:bg-emerald-500/20 shadow-[0_0_30px_-10px_rgba(16,185,129,0.3)]' :
                                        'border-amber-500/50 bg-amber-500/10 hover:bg-amber-500/20 shadow-[0_0_30px_-10px_rgba(245,158,11,0.3)]'
                                    }`}
                                onClick={togglePause}
                            >
                                {isPaused ? <Play className="h-6 w-6 fill-current" /> : <Pause className="h-6 w-6 fill-current" />}
                            </Button>

                            <Button
                                size="icon"
                                className="h-20 w-20 rounded-full bg-gradient-to-tr from-rose-500 to-red-600 hover:from-rose-400 hover:to-red-500 shadow-[0_10px_40px_-10px_rgba(244,63,94,0.5)] transition-all hover:scale-105 active:scale-95 border-0 ring-4 ring-rose-500/10"
                                onClick={clockOut}
                            >
                                <StopCircle className="h-8 w-8 text-white fill-white" />
                            </Button>
                        </>
                    )}
                </div>

                <div className="text-center text-xs font-medium text-zinc-600">
                    {status === 'OUT' ? 'Have a productive day' : `Started at ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
                </div>
            </div>
        </div>
    );
}
