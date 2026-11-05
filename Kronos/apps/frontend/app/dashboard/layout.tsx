'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, PieChart, LogOut, Clock } from 'lucide-react';
import { createClient } from '@/utils/supabase/client';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname();
    const router = useRouter();
    const supabase = createClient();

    const handleLogout = async () => {
        await supabase.auth.signOut();
        router.push('/login');
    };

    const navigation = [
        { name: 'Time Tracker', href: '/dashboard', icon: Clock },
        { name: 'Reports', href: '/dashboard/reports', icon: PieChart },
    ];

    return (
        <div className="flex bg-brand-navy min-h-screen text-white font-sans antialiased selection:bg-brand-gold/30">
            {/* Sidebar */}
            <aside className="w-64 border-r border-white/5 bg-brand-navy/80 backdrop-blur-xl flex flex-col fixed inset-y-0 z-50">
                <div className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-brand-gold to-yellow-600 flex items-center justify-center shadow-lg shadow-brand-gold/20">
                            <LayoutDashboard className="h-5 w-5 text-brand-navy" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-brand-gold">
                            Tavilga Cronos
                        </span>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-4 space-y-1">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`
                                    flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group
                                    ${isActive
                                        ? 'bg-white/10 text-brand-gold shadow-inner shadow-white/5'
                                        : 'text-zinc-500 hover:text-white hover:bg-white/5'}
                                `}
                            >
                                <item.icon className={`h-5 w-5 transition-colors ${isActive ? 'text-brand-gold' : 'text-zinc-600 group-hover:text-zinc-400'}`} />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-white/5">
                    <button
                        onClick={handleLogout}
                        className="flex w-full items-center gap-3 px-4 py-3 rounded-xl text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 group"
                    >
                        <LogOut className="h-5 w-5 transition-colors text-zinc-600 group-hover:text-red-400" />
                        <span className="font-medium">Sign Out</span>
                    </button>
                    <div className="mt-4 px-4 text-xs text-zinc-700 text-center">
                        © 2026 Tavilga
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-64 min-h-screen bg-brand-navy relative">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-gold/10 via-brand-navy/0 to-zinc-950/0 pointer-events-none" />

                {/* Logo Corporativo */}
                <div className="absolute top-6 right-6 z-40">
                    <Image src="/logo.png" alt="Quantigrade Logo" width={96} height={24} className="h-1.5 w-auto opacity-60 hover:opacity-100 transition-opacity" />
                </div>

                <div className="relative z-10 p-6">
                    {children}
                </div>
            </main>
        </div>
    );
}
