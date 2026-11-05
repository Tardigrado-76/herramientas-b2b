# COMPLIANCE SENTINEL — GRC-as-a-Code para DORA, NIS2, ENS y EU AI Act

Plataforma ejecutiva con interfaz web moderna en **Streamlit** y acceso directo ejecutable doble clic para Windows (`.lnk` y `.bat`), implementando el ecosistema de **Gobernanza Continua, Gestión de Riesgo y Cumplimiento Técnico** en estricto cumplimiento con:
- **DORA** (Reglamento UE 2022/2554 de Resiliencia Operativa Digital Financiera)
- **NIS2** (Directiva UE 2022/2555 de Ciberseguridad Europea)
- **ENS** (Esquema Nacional de Seguridad Categoría Alta - RD 311/2022)
- **RGPD / GDPR** (Reglamento UE 2016/679)
- **CRA** (Reglamento UE 2024/2847 de Ciberresiliencia y Cadena SBOM)
- **EU AI Act** (Reglamento UE 2024/1689 de Inteligencia Artificial con supervisión HITL)

---

## 🚀 Inicio Rápido (Doble Clic)

En la raíz del proyecto dispones de dos opciones de inicio instantáneo:

1. **`COMPLIANCE_SENTINEL.lnk`**: Acceso directo con icono de escudo de seguridad de Windows (doble clic).
2. **`INICIAR_COMPLIANCE_SENTINEL.bat`**: Script batch que inicia el servidor Streamlit en `http://localhost:8505` y abre automáticamente tu navegador web.

O por terminal:
```powershell
streamlit run app_streamlit.py --server.port 8505
```

---

## 🏛️ Consejo Regulador de 4 Jueces IA

- ⚖️ **CISO Lead Judge**: Presidente del Consejo Regulador que sintetiza dictámenes formales para el Comité de Dirección.
- 🛡️ **NIS2 Sentinel**: Auditor de gestión de riesgos cibernéticos, continuidad operativa y avisos tempranos al CSIRT (< 24h).
- 🔒 **GDPR Privacy Auditor**: Delegado de Protección de Datos (DPO) que audita Medidas Técnicas y Organizativas (TOMs) y Evaluaciones de Impacto (EIPD/DPIA).
- 📦 **CRA SecOps**: Validador de la cadena de suministro de software, verificación de dependencias y generación de SBOM estándar CycloneDX v1.5 JSON.

---

## 📊 Módulos de la Aplicación Web (Streamlit)

1. **📊 Dashboard CISO & Diagnóstico**:
   - Tarjetas de estado global europeo, porcentaje de conformidad por marco normativo y resumen del sello Merkle activo.
   - Matriz técnica de cumplimiento de DORA, NIS2, ENS Alta, RGPD, CRA y EU AI Act.

2. **🚀 Ejecutar Auditoría GRC-as-a-Code**:
   - Selector interactivo de controles de producción (MFA, backups inmutables, alertas CSIRT, TLS 1.3, RAT/EIPD, SBOM y CVEs).
   - Invocación en tiempo real del Consejo de Jueces para emisión de acta.

3. **🧱 Búnker Merkle de Evidencias**:
   - Visualizador de la estructura jerárquica del Árbol de Merkle (Merkle Root Hash SHA-256) bajo estándar SLSA Nivel 3+.
   - Validador criptográfico instantáneo de actas contra manipulación o alteración.

4. **📋 Plan de Remediación & Backlog**:
   - Conversión automática de brechas a tareas técnicas de ingeniería con plazos recomendados en días y nivel de criticidad.

5. **📑 Dictamen Ejecutivo Oficial**:
   - Dictamen formal de peritaje regulatorio listo para presentar ante el Consejo de Administración o auditores externos (descargable en Markdown).

---

## 🧪 Verificación de Pruebas Unitarias

Ejecutado con 100% de éxito:
```powershell
python -m unittest discover -s "tests" -p "test_*.py" -v
```
*(7 tests unitarios e integrados pasando con éxito en 0.04s)*
