import Link from 'next/link';
import { Clock, Shield, CheckCircle2, ChevronRight, BarChart3, Database } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#020b14] text-white font-sans antialiased relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-yellow-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-[600px] h-[600px] bg-blue-900/20 rounded-full blur-[150px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="border-b border-white/5 bg-[#020b14]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-[#d4af37] to-[#f3e5ab] flex items-center justify-center shadow-lg shadow-yellow-600/20">
              <Clock className="h-5 w-5 text-[#020b14]" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-[#d4af37] tracking-tight">
              Tavilga Cronos
            </span>
          </div>

          <Link 
            href="/login" 
            className="px-5 py-2.5 rounded-xl border border-white/10 hover:border-[#d4af37]/50 hover:bg-[#d4af37]/5 text-sm font-semibold transition-all duration-300 flex items-center gap-2 group"
          >
            Acceso Empleados
            <ChevronRight className="h-4 w-4 text-[#d4af37] group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-20 lg:py-32 relative z-10">
        <div className="grid lg:grid-cols-12 gap-16 items-center">
          
          {/* Left Column: Copy */}
          <div className="lg:col-span-7 flex flex-col gap-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#d4af37]/10 border border-[#d4af37]/20 text-[#d4af37] text-xs font-semibold uppercase tracking-wider w-fit">
              <Shield className="h-3.5 w-3.5" /> Cumplimiento Normativo 2025 Obligatorio
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-tight">
              El control de <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-[#d4af37]">presencia digital</span> para equipos de alto rendimiento.
            </h1>

            <p className="text-zinc-400 text-lg md:text-xl leading-relaxed max-w-2xl">
              Tavilga Cronos automatiza el registro horario obligatorio de tus empleados en España, garantizando inmutabilidad criptográfica, políticas de geofencing inteligente y soporte offline completo.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <Link 
                href="/login" 
                className="px-8 py-4 bg-gradient-to-tr from-[#d4af37] to-[#e6c655] hover:opacity-95 text-[#020b14] font-bold rounded-xl shadow-lg shadow-yellow-600/10 hover:shadow-yellow-600/20 transition-all text-center flex items-center justify-center gap-2"
              >
                Comenzar Fichaje
              </Link>
              <a 
                href="#features" 
                className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 font-semibold rounded-xl transition-all text-center flex items-center justify-center"
              >
                Saber Más
              </a>
            </div>

            {/* Micro badges */}
            <div className="flex flex-wrap items-center gap-x-8 gap-y-3 mt-4 border-t border-white/5 pt-8 text-sm text-zinc-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-[#d4af37]" /> Ley de Registro Horario
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-[#d4af37]" /> Cifrado de Extremo a Extremo
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-[#d4af37]" /> Verificación de Ubicación
              </div>
            </div>
          </div>

          {/* Right Column: Visual Dashboard Preview */}
          <div className="lg:col-span-5 relative">
            <div className="relative rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-xl p-8 shadow-2xl shadow-black/40 overflow-hidden group hover:border-[#d4af37]/30 transition-all duration-500">
              <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-500/10 rounded-full blur-2xl pointer-events-none" />
              
              {/* Header Simulation */}
              <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-6">
                <div>
                  <h3 className="font-bold text-lg">Panel de Empleado</h3>
                  <p className="text-xs text-zinc-500">Estado de la sesión activa</p>
                </div>
                <div className="h-3.5 w-3.5 rounded-full bg-emerald-500 animate-pulse" />
              </div>

              {/* Stats Simulation */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <span className="text-xs text-zinc-500 block mb-1">Horas Hoy</span>
                  <span className="text-2xl font-bold font-mono">07:42:15</span>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <span className="text-xs text-zinc-500 block mb-1">Pausas Acum.</span>
                  <span className="text-2xl font-bold font-mono text-amber-500">00:30:00</span>
                </div>
              </div>

              {/* Action Button Simulation */}
              <div className="flex flex-col gap-3">
                <div className="w-full py-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-semibold text-center text-sm">
                  Sesión Iniciada con Éxito
                </div>
                <div className="w-full py-3 bg-white/5 border border-white/5 text-zinc-400 text-xs text-center rounded-lg">
                  IP Registrada: <span className="font-mono text-zinc-300">192.168.1.155</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Features Grid */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-24 border-t border-white/5 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16 flex flex-col gap-4">
          <h2 className="text-3xl md:text-4xl font-extrabold">Diseñado para la máxima seguridad corporativa</h2>
          <p className="text-zinc-400 text-base md:text-lg">
            Cronos no es solo una hoja de cálculo digital. Cumple los estándares exigidos para auditorías gubernamentales en 2025.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Card 1 */}
          <div className="p-8 rounded-2xl bg-white/[0.01] border border-white/5 hover:border-white/10 transition-all duration-300 flex flex-col gap-4">
            <div className="h-12 w-12 rounded-xl bg-[#d4af37]/10 flex items-center justify-center text-[#d4af37]">
              <Shield className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Inmutabilidad Absoluta</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Triggers a nivel de base de datos impiden la alteración o borrado de cualquier registro histórico de fichaje de forma retrospectiva.
            </p>
          </div>

          {/* Card 2 */}
          <div className="p-8 rounded-2xl bg-white/[0.01] border border-white/5 hover:border-white/10 transition-all duration-300 flex flex-col gap-4">
            <div className="h-12 w-12 rounded-xl bg-[#d4af37]/10 flex items-center justify-center text-[#d4af37]">
              <Database className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Validación Geofencing</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Comprobación inteligente en backend mediante geolocalización. Asegura el fichaje presencial dentro del perímetro autorizado de tus sedes.
            </p>
          </div>

          {/* Card 3 */}
          <div className="p-8 rounded-2xl bg-white/[0.01] border border-white/5 hover:border-white/10 transition-all duration-300 flex flex-col gap-4">
            <div className="h-12 w-12 rounded-xl bg-[#d4af37]/10 flex items-center justify-center text-[#d4af37]">
              <BarChart3 className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Sincronización Offline</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Ficha sin conexión a internet. Los datos se almacenan localmente de forma cifrada y se sincronizan al recuperar cobertura con firmas seguras.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-[#01060c] py-12 text-center text-sm text-zinc-600 relative z-10">
        <p>© 2026 Tavilga. Todos los derechos reservados. Desarrollado conforme al Estatuto de los Trabajadores Art. 34.9.</p>
      </footer>
    </div>
  );
}
