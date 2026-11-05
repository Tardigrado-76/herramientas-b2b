# OUTBOUND MACHINE — Motor B2B Autónomo de Prospección y Cierre

Plataforma ejecutiva con interfaz web moderna en **Streamlit** y acceso directo ejecutable doble clic para Windows (`.lnk` y `.bat`), implementando el motor de prospección B2B y cierre asistido en estricto cumplimiento con **NIS2 (Directiva UE 2022/2555)**, **RGPD (Reglamento UE 2016/679)** y **CRA (Reglamento UE 2024/2847)**.

---

## 🚀 Inicio Rápido (Doble Clic)

En la raíz del proyecto dispones de dos opciones de inicio instantáneo:

1. **`OUTBOUND_MACHINE.lnk`**: Acceso directo con icono de radar/objetivo de Windows (doble clic).
2. **`INICIAR_OUTBOUND_MACHINE.bat`**: Script batch que inicia el servidor Streamlit en `http://localhost:8504` y abre automáticamente tu navegador web.

O por terminal:
```powershell
streamlit run app_streamlit.py --server.port 8504
```

---

## 🏛️ Enjambre de 4 Agentes SDR Autónomos

- 🎯 **SDR Director**: Orquestador de la estrategia de prospección, cadencias multicanal y supervisión de conversiones.
- 🔍 **Tech Researcher**: Análisis OSINT profundo, cualificación ICP (score 0-100) e inferencia de emails corporativos.
- ✍️ **Sales Copywriter**: Redacción de correos con ganchos hiperextremos de alto impacto, libres de spam y con valor técnico.
- 🛡️ **Objection Handler**: Clasificación de sentimiento en respuestas entrantes y activación inmediata de handoff hacia el comercial humano ante interés o petición de reunión.

---

## 📊 Módulos de la Aplicación Web (Streamlit)

1. **🎯 Generador & Auditor de Prospección**:
   - Selector de presets corporativos (Fintech, Healthcare, SaaS) o entrada personalizada.
   - Cualificación ICP automática (Tier 1, 2, 3), normalización de dominio y borrador de Touch 1 con token RGPD.

2. **📊 Embudo & Cadencia de Secuencias**:
   - Desglose cronológico de la cadencia de 3 toques (Día 1: Gancho, Día 4: Caso de éxito, Día 8: Breakup).
   - Métricas de leads cualificados y tabla de empresas prospectadas.

3. **🚨 Respuestas & Handoff Humano**:
   - Simulador de respuestas de prospectos entrantes con detección de sentimiento y activación de alerta comercial.

4. **📜 Auditoría Criptográfica NIS2**:
   - Registro inmutable de cada despacho de correo con hash SHA-256 encadenado (Art. 21 y 23).

5. **🛡️ Seguridad CRA & RGPD**:
   - Software Bill of Materials (SBOM) CycloneDX v1.5 JSON descargable.
   - Firewall anti-inyecciones y anti-phishing para prospección comercial.
   - Comprobador de Lista Robinson y registro de derecho de oposición (Opt-Out).

---

## 🧪 Verificación de Pruebas Unitarias

Ejecutado con 100% de éxito:
```powershell
python -m unittest discover -s "tests" -p "test_*.py" -v
```
*(14 tests unitarios e integrados pasando con éxito en 0.29s)*
