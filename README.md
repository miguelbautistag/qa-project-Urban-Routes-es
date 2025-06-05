# Proyecto Urban Routes - Automatización de Solicitud de Taxi  
**Autor:** Miguel Bautista Gómez  
**Sprint:** 8  
**Cohort:** 28  

## Descripción del Proyecto  
Este proyecto automatiza el flujo completo de solicitud de un taxi en la aplicación **Urban Routes**.  
Las pruebas replican las acciones de un usuario real al pedir un taxi, validando que la aplicación responda correctamente en cada etapa del proceso: elección de ruta, tarifa, verificación telefónica, método de pago, solicitudes adicionales y confirmación del servicio.

## Tecnologías y Técnicas Utilizadas  

**Lenguaje:**  
- Python 3.13

**Librerías:**  
- `selenium` – Utilizada para interactuar con los elementos de la aplicación desde el navegador.  
- `pytest` – Para estructurar y ejecutar las pruebas automatizadas.

**Técnicas:**  
- Automatización E2E (End to End) usando Selenium WebDriver.  
- Patrón de diseño Page Object Model (POM).  
- Validación del código de confirmación a través del log de red (`driver.get_log('performance')`).  
- Uso de esperas explícitas (`WebDriverWait`) y condiciones esperadas (`expected_conditions`).  
- Validación de la interfaz gráfica mediante asserts.

## Pruebas Incluidas  

Las pruebas están implementadas en el archivo `test_urban_routes.py` y comprenden los siguientes escenarios:

1. **Ingreso de direcciones** – Valida que se guarde correctamente el origen y destino.  
2. **Selección de tarifa Comfort** – Automatiza el clic sobre la opción de tarifa intermedia.  
3. **Ingreso de número de teléfono y verificación por código** – Simula el flujo de autenticación.  
4. **Ingreso de método de pago (tarjeta)** – Automatiza el ingreso de tarjeta y cierra el modal.  
5. **Mensaje al conductor** – Simula enviar un comentario antes del viaje.  
6. **Solicitudes adicionales** – Activa cobija, pañuelos.
7. **Solicitudes adicionales** – Selecciona helados.  
8. **Confirmación del servicio** – Hace clic en el botón de solicitud final del taxi.  

> El código de confirmación es recuperado automáticamente usando el método `retrieve_phone_code()`.

## Cómo ejecutar las pruebas desde la consola  

Desde la terminal (GitBash), navega a la carpeta raíz del proyecto y ejecuta:

```bash
pytest test_urban_routes.py -s