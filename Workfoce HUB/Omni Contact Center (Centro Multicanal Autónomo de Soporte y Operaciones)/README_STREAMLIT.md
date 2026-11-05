# OMNI CONTACT — Contact Center IA Multimodal

Plataforma ejecutiva con interfaz web moderna en **Streamlit** y acceso directo ejecutable doble clic para Windows (`.lnk` y `.bat`), implementando el ecosistema de **Contact Center IA Multimodal Autónomo** en estricto cumplimiento con **NIS2 (Directiva UE 2022/2555)**, **RGPD (Reglamento UE 2016/679)** y **CRA (Reglamento UE 2024/2847)**.

---

## 🚀 Inicio Rápido (Doble Clic)

En la raíz del proyecto dispones de dos opciones de inicio instantáneo:

1. **`OMNI_CONTACT.lnk`**: Acceso directo con icono telefónico de Windows (doble clic).
2. **`INICIAR_OMNI_CONTACT.bat`**: Script batch que inicia el servidor Streamlit en `http://localhost:8503` y abre automáticamente tu navegador web.

O por terminal:
```powershell
streamlit run app_streamlit.py --server.port 8503
```

---

## 📡 Canales Integrados & Adaptadores Normalizados

- 📞 **Voz SIP / WebRTC**: Recepción de eventos de llamada, barge-in y síntesis de voz neuronal (TTS).
- 💬 **WhatsApp Cloud API**: Integración conversacional interactiva.
- 🌐 **Web Chat Live**: Interfaz de chat web con historial de sesión y asignación dinámica.
- ✉️ **Email Support**: Ticketing estructurado y respuestas ejecutivas automáticas.

---

## 👥 Personas y Roles Multimodales Especializados

1. 🤖 **Receptionist_Triage**: Saludo institucional, captura y registro de consentimiento RGPD (Art. 6/7) y triaje inicial.
2. 💳 **Billing_Specialist**: Resolución de discrepancias en facturas, políticas de reembolso y suscripciones.
3. 🛠️ **Technical_Support_Tier1**: Diagnóstico de conectividad, configuración de troncales SIP y guías paso a paso.
4. 🚨 **Supervisor_Escalation**: Intervención inmediata ante picos de frustración (score >= 60/100) y quejas de clientes VIP.

---

## 📊 Módulos de la Aplicación Web (Streamlit)

1. **🎙️ Simulador Multicanal en Vivo**:
   - Selección de canal (Voz SIP, WhatsApp, WebChat, Email) y verificación de consentimiento RGPD.
   - Diálogo conversacional interactivo con enrutamiento dinámico en tiempo real y badges de sentimiento.

2. **📊 Panel de Telemetría & Sentimiento**:
   - Métricas de volumen de llamadas, eventos en ledger, tasa de autorresolución autónoma y tabla de sesiones.

3. **🚨 Escalaciones a Supervisor**:
   - Panel de control de crisis con detección automática de clientes de alto riesgo o solicitudes de escalación.

4. **📜 Auditoría Criptográfica NIS2**:
   - Verificación de la cadena SHA-256 no repudiable para telecomunicaciones (Art. 21 y 23).

5. **🛡️ Seguridad CRA & RGPD**:
   - Software Bill of Materials (SBOM) CycloneDX v1.5 JSON descargable.
   - Firewall de prompt injection para telefonía y purga/triturado criptográfico de llamadas (Art. 17).

---

## 🧪 Verificación de Pruebas Unitarias

Ejecutado con 100% de éxito:
```powershell
python -m unittest discover -s "tests" -p "test_*.py" -v
```
*(14 tests unitarios e integrados pasando con éxito)*
