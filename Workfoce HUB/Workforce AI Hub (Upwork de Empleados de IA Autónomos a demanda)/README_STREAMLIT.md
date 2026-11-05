# WORKFORCE AI HUB — Aplicación Ejecutiva Streamlit

Plataforma ejecutiva con interfaz web moderna en **Streamlit** y acceso directo ejecutable doble clic para Windows (`.lnk` y `.bat`), implementando el ecosistema del **Upwork de Empleados de IA Autónomos a Demanda** en estricto cumplimiento con **NIS2 (Directiva UE 2022/2555)**, **RGPD (Reglamento UE 2016/679)** y **CRA (Reglamento UE 2024/2847)**.

---

## 🚀 Inicio Rápido (Doble Clic)

En la raíz del proyecto dispones de dos accesos directos:

1. **`WORKFORCE_AI_HUB.lnk`**: Acceso directo con icono nativo de Windows (doble clic).
2. **`INICIAR_WORKFORCE_AI.bat`**: Script batch que arranca el servidor Streamlit en `http://localhost:8502` y abre tu navegador web automáticamente.

O bien directamente por consola:
```powershell
streamlit run app_streamlit.py --server.port 8502
```

---

## 👥 Plantilla de 8 Empleados IA Autónomos + Chief of Staff

1. 👑 **Chief_of_Staff**: Orquestación y descomposición de tareas complejas, síntesis ejecutiva.
2. 🚀 **GTM_Engineer**: Automatización de funnels, integración de webhooks CRM y telemetría.
3. 🔍 **SEO_AEO_Specialist**: Optimización para motores de respuesta (Perplexity, Claude, SGE) y Schema.org.
4. 💻 **FullStack_WebDev**: Endpoints FastAPI, frontend responsivo y desarrollo ágil.
5. 📱 **Social_Media_Manager**: Calendarios multicanal (LinkedIn, X/Twitter, Threads) y copywriting.
6. 🎯 **Ad_Manager**: Copywriting publicitario, pruebas A/B multivariantes y modelado de ROAS.
7. 💼 **Sales_Representative**: Secuencias frías salientes B2B, calificación ICP (BANT) y objeciones.
8. 🤝 **Customer_Satisfaction**: Resolución empática de tickets, desescalada y directrices de soporte.

---

## 📊 Módulos de la Aplicación Web (Streamlit)

1. **👥 Catálogo de Empleados IA**:
   - Tarjetas informativas de cada rol con delimitación de capacidades, cuota de horas y estado de contratación.
   - Contratación de empleados a golpe de un clic con asignación de SLA.

2. **⚡ Despacho Autónomo de Tareas**:
   - Enrutamiento semántico inteligente automático hacia el empleado óptimo.
   - Generación de entregables especializados con control de calidad (Quality Gate) y puntuación automática.

3. **📈 Panel de Ejecución & Telemetría**:
   - Métricas de tareas ejecutadas, tokens consumidos, coste estimado de inferencia y tabla de intervenciones.

4. **📜 Auditoría Criptográfica NIS2**:
   - Verificación de integridad de la cadena de bloques SHA-256 no repudiable (Art. 21 y 23).

5. **🛡️ Seguridad CRA & RGPD**:
   - Generador y descargador del SBOM estándar CycloneDX v1.5 JSON.
   - Simulador de firewall contra inyecciones de prompt.
   - Simulador de purga de datos personales (PII) y botón de triturado criptográfico (Art. 17).

---

## 🧪 Verificación de Pruebas Unitarias

Ejecutado con 100% de éxito:
```powershell
python -m unittest discover -s "tests" -p "test_*.py" -v
```
*(14 tests pasando con éxito)*
