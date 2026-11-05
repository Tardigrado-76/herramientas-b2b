# PRD — Kronos Enterprise Workforce & Time-Tracking (100% Production Ready)

## Objetivo
Certificar el monorepo **Kronos** (`apps/backend` NestJS 11 + `apps/frontend` Next.js 16) al **100% Production Ready** bajo arquitectura **Cero-Docker Absoluto**, conectándose directamente al pooler remoto de Supabase Cloud y superando todas las auditorías TDD y Code Doctor.

## Checklist de Hitos (Ralph Loop)
- [x] **M1. Desacoplamiento Cero-Docker**: Neutralización de `docker-compose.yml`, `docker-compose.prod.yml` y `Dockerfile`s en favor de ejecución nativa Node.js v20+ y conexión directa a Supabase Cloud Pooler (`aws-0-eu-north-1.pooler.supabase.com`).
- [x] **M2. Auditoría Code Doctor (Backend)**: Corrección de 465 problemas de ESLint/Prettier, tipado estricto en controladores/servicios (`TimeTrackingService`, `TimeTrackingController`, `SupabaseService`, `main.ts`) y eliminación de imports muertos.
- [x] **M3. Auditoría Code Doctor (Frontend)**: Reemplazo de `interface InputProps` vacía por `type InputProps` en `components/ui/input.tsx`, migración a `<Image />` de Next.js en `app/dashboard/layout.tsx`, y resolución de dependencias de React Hooks (`use-time-tracker.ts`, `stats-widgets.tsx`).
- [x] **M4. Suite TDD Backend (Jest)**: 6 suites y 17 tests unitarios validando la fórmula de Haversine para geocerca de 500m, máquina de estados de fichaje (`IN -> PAUSE_IN -> PAUSE_OUT -> OUT`), `SupabaseStrategy` con mocks de autenticación y `TimeTrackingController`.
- [x] **M5. Suite TDD Frontend**: Validación automatizada de formateo de temporizador, firma criptográfica de cola offline (`localStorage`) y componentes UI ejecutándose desde la raíz con `npm test`.
- [x] **M6. Lanzador Nativo Windows**: Creación de `INICIAR_KRONOS_HUB.bat` con soporte UTF-8 (`chcp 65001 >nul`).
