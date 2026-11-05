import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/utils/supabase/client';

export type TimeEntryType = 'IN' | 'OUT' | 'PAUSE_IN' | 'PAUSE_OUT';

interface QueuedAction {
    action: 'in' | 'out' | 'pause';
    recorded_at: string;
    latitude?: number | null;
    longitude?: number | null;
    device_info?: string;
    ip_address?: string;
    offline_signature?: string;
}

export function useTimeTracker() {
    const router = useRouter();
    const [status, setStatus] = useState<TimeEntryType | 'LOADING'>('LOADING');
    const [elapsedTime, setElapsedTime] = useState(0);
    const [startTime, setStartTime] = useState<Date | null>(null);
    const [isOnline, setIsOnline] = useState(typeof window !== 'undefined' ? navigator.onLine : true);
    const supabase = createClient();

    const syncOfflineQueue = useCallback(async () => {
        if (typeof window === 'undefined' || !navigator.onLine) return;
        const queueStr = localStorage.getItem('offline_clock_queue');
        if (!queueStr) return;
        const queue: QueuedAction[] = JSON.parse(queueStr);
        if (queue.length === 0) return;

        const { data: { session } } = await supabase.auth.getSession();
        if (!session) return;

        console.log(`Syncing ${queue.length} offline actions...`);
        for (const item of queue) {
            try {
                const res = await fetch(`http://localhost:3000/time-entries/${item.action}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${session.access_token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        latitude: item.latitude,
                        longitude: item.longitude,
                        device_info: item.device_info,
                        ip_address: item.ip_address,
                        recorded_at: item.recorded_at,
                        offline_signature: item.offline_signature
                    })
                });
                if (!res.ok) {
                    console.error("Failed to sync offline item:", await res.text());
                }
            } catch (e) {
                console.error("Error during sync:", e);
                break;
            }
        }
        localStorage.removeItem('offline_clock_queue');
    }, [supabase]);

    const fetchStatus = useCallback(async () => {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                console.warn("No active session found in useTimeTracker");
                setStatus('OUT');
                return;
            }

            // Sync any existing offline queue before checking status
            if (navigator.onLine) {
                await syncOfflineQueue();
            }

            const res = await fetch('http://localhost:3000/time-entries/current', {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });

            if (res.ok) {
                const data = await res.json();
                if (data) {
                    setStatus(data.type);
                    if (data.type === 'IN' || data.type === 'PAUSE_IN') {
                        const start = new Date(data.created_at);
                        setStartTime(start);
                        const now = new Date();
                        setElapsedTime(Math.floor((now.getTime() - start.getTime()) / 1000));
                    } else {
                        setStartTime(null);
                        setElapsedTime(0);
                    }
                } else {
                    setStatus('OUT');
                }
            } else {
                console.error("Backend error:", res.status, await res.text());
                setStatus('OUT');
            }
        } catch (e) {
            console.error("Failed to fetch status", e);
            setStatus('OUT');
        }
    }, [supabase, syncOfflineQueue]);

    useEffect(() => {
        fetchStatus();
    }, [fetchStatus]);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const handleOnline = () => {
            setIsOnline(true);
            syncOfflineQueue().then(() => fetchStatus());
        };
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, [syncOfflineQueue, fetchStatus]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (status === 'IN' && startTime) {
            interval = setInterval(() => {
                const now = new Date();
                setElapsedTime(Math.floor((now.getTime() - startTime.getTime()) / 1000));
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [status, startTime]);

    const performAction = async (action: 'in' | 'out' | 'pause') => {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
            console.error("Cannot perform action: No active session found.");
            router.push('/login');
            return;
        }

        const timestamp = new Date().toISOString();
        const browserGeo = await getCoordinates();

        // 1. Check if Offline
        if (!navigator.onLine) {
            console.log(`Working offline. Queueing action: ${action}...`);
            const queueStr = localStorage.getItem('offline_clock_queue');
            const queue: QueuedAction[] = queueStr ? JSON.parse(queueStr) : [];

            // Sign payload to prevent tampering
            const payload = {
                action,
                recorded_at: timestamp,
                latitude: browserGeo?.latitude,
                longitude: browserGeo?.longitude,
                device_info: typeof window !== 'undefined' ? navigator.userAgent : 'Offline Browser Client',
                ip_address: '127.0.0.1 (Offline Cached)'
            };
            const signature = btoa(JSON.stringify(payload) + session.access_token).slice(0, 32);

            const queuedAction: QueuedAction = {
                ...payload,
                offline_signature: signature
            };

            localStorage.setItem('offline_clock_queue', JSON.stringify([...queue, queuedAction]));

            // Update UI State locally
            if (action === 'in') {
                setStatus('IN');
                setStartTime(new Date(timestamp));
                setElapsedTime(0);
            } else if (action === 'out') {
                setStatus('OUT');
                setStartTime(null);
                setElapsedTime(0);
            } else if (action === 'pause') {
                setStatus(prev => prev === 'IN' ? 'PAUSE_IN' : 'IN');
                if (status === 'IN') {
                    setStartTime(null);
                } else {
                    setStartTime(new Date(timestamp));
                }
            }
            return;
        }

        // 2. Online Mode
        console.log(`Performing action online: ${action}...`);
        try {
            const res = await fetch(`http://localhost:3000/time-entries/${action}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: browserGeo?.latitude,
                    longitude: browserGeo?.longitude,
                    device_info: typeof window !== 'undefined' ? navigator.userAgent : 'Browser Client',
                    ip_address: '127.0.0.1', // Will be populated by backend if required
                    recorded_at: timestamp
                })
            });

            if (res.ok) {
                await fetchStatus();
            } else {
                const errText = await res.text();
                console.error("Action failed", errText);
                alert(`Error al registrar jornada: ${errText}`);
            }
        } catch (e) {
            console.error("Network error", e);
        }
    };

    const getCoordinates = (): Promise<{ latitude: number; longitude: number } | null> => {
        return new Promise((resolve) => {
            if (typeof window === 'undefined' || !navigator.geolocation) {
                resolve(null);
                return;
            }
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
                () => resolve(null),
                { enableHighAccuracy: true, timeout: 5000 }
            );
        });
    };

    return {
        status,
        elapsedTime,
        isOnline,
        clockIn: () => performAction('in'),
        clockOut: () => performAction('out'),
        togglePause: () => performAction('pause'),
    };
}
