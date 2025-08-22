#!/bin/bash

# Script para monitorear el sistema FIFO
# Ejecutar: chmod +x monitor_fifo.sh && ./monitor_fifo.sh

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MONITOR DEL SISTEMA FIFO${NC}"
echo "========================================"

# Función para verificar estado
check_status() {
    echo -e "\n${YELLOW}📊 Estado del Sistema:${NC}"
    
    # Verificar contenedores
    echo -e "${BLUE}Contenedores activos:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep webhook_personal
    
    # Verificar health
    echo -e "\n${BLUE}Health check:${NC}"
    curl -s http://localhost:5050/api/health && echo " ✅" || echo " ❌"
    
    # Verificar estado de cola
    echo -e "\n${BLUE}Estado de cola FIFO:${NC}"
    curl -s http://localhost:5050/api/queue/status | python3 -m json.tool 2>/dev/null || echo "❌ Error obteniendo estado"
}

# Función para mostrar logs filtrados
show_fifo_logs() {
    echo -e "\n${YELLOW}📋 Logs del Sistema FIFO (últimos 50):${NC}"
    docker logs webhook_personal-app-1 --tail 50 | grep -E "(FIFO|WebSocket|PROCESANDO|COMPLETADO|AÑADIDO|MessageQueueService|procesador|cola)" || echo "No hay logs FIFO recientes"
}

# Función para monitoreo en tiempo real
monitor_realtime() {
    echo -e "\n${YELLOW}🔴 Monitoreo en tiempo real (Ctrl+C para salir):${NC}"
    echo "Filtrando logs relacionados con FIFO, WebSocket y procesamiento..."
    docker logs webhook_personal-app-1 -f | grep --line-buffered -E "(FIFO|WebSocket|PROCESANDO|COMPLETADO|AÑADIDO|MessageQueueService|procesador|cola)"
}

# Función para probar el sistema
test_system() {
    echo -e "\n${YELLOW}🧪 Probando sistema FIFO:${NC}"
    
    # Test de cola
    echo "Enviando mensaje de prueba a cola..."
    curl -s -X POST http://localhost:5050/api/queue/test | python3 -m json.tool 2>/dev/null || echo "❌ Error en test"
    
    # Esperar un momento
    echo "Esperando 3 segundos..."
    sleep 3
    
    # Verificar longitudes
    echo "Verificando longitudes de cola..."
    curl -s http://localhost:5050/api/queue/lengths | python3 -m json.tool 2>/dev/null || echo "❌ Error obteniendo longitudes"
}

# Menú principal
while true; do
    echo -e "\n${GREEN}Selecciona una opción:${NC}"
    echo "1) 📊 Verificar estado del sistema"
    echo "2) 📋 Mostrar logs FIFO recientes"
    echo "3) 🔴 Monitoreo en tiempo real"
    echo "4) 🧪 Probar sistema FIFO"
    echo "5) 📱 Simular webhook de WhatsApp"
    echo "6) 🧹 Limpiar pantalla"
    echo "7) ❌ Salir"
    
    read -p "Opción (1-7): " choice
    
    case $choice in
        1)
            check_status
            ;;
        2)
            show_fifo_logs
            ;;
        3)
            monitor_realtime
            ;;
        4)
            test_system
            ;;
        5)
            echo -e "\n${YELLOW}📱 Simulando webhook de WhatsApp...${NC}"
            curl -s -X POST http://localhost:5050/webhook \
                -H "Content-Type: application/json" \
                -d '{
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "test_entry",
                        "changes": [{
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "573219306305",
                                    "phone_number_id": "723278304205850"
                                },
                                "contacts": [{
                                    "profile": {"name": "Usuario de Prueba"},
                                    "wa_id": "573103391854"
                                }],
                                "messages": [{
                                    "from": "573103391854",
                                    "id": "test_msg_'$(date +%s)'",
                                    "timestamp": "'$(date +%s)'",
                                    "text": {"body": "Mensaje de prueba del monitor"},
                                    "type": "text"
                                }]
                            },
                            "field": "messages"
                        }]
                    }]
                }' && echo -e "\n✅ Webhook enviado" || echo -e "\n❌ Error enviando webhook"
            ;;
        6)
            clear
            echo -e "${BLUE}🚀 MONITOR DEL SISTEMA FIFO${NC}"
            echo "========================================"
            ;;
        7)
            echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opción inválida${NC}"
            ;;
    esac
done