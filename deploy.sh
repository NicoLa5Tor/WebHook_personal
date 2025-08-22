 
#!/bin/bash

# Script de despliegue para WhatsApp API Service
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker y Docker Compose están instalados
check_dependencies() {
    print_status "Verificando dependencias..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    
    print_status "Dependencias verificadas ✓"
}

# Verificar archivo .env
check_env_file() {
    print_status "Verificando archivo .env..."
    
    if [ ! -f .env ]; then
        print_warning "Archivo .env no encontrado. Creando desde .env.production..."
        cp .env.production .env
        print_error "IMPORTANTE: Edita el archivo .env con tus credenciales reales antes de continuar"
        exit 1
    fi
    
    # Verificar variables críticas
    if ! grep -q "ACCESS_TOKEN=" .env || grep -q "tu_access_token_aqui" .env; then
        print_error "Configura ACCESS_TOKEN en el archivo .env"
        exit 1
    fi
    
    if ! grep -q "PHONE_NUMBER_ID=" .env || grep -q "tu_phone_number_id_aqui" .env; then
        print_error "Configura PHONE_NUMBER_ID en el archivo .env"
        exit 1
    fi
    
    print_status "Archivo .env verificado ✓"
}

# Construir imágenes
build_images() {
    print_status "Construyendo imágenes Docker..."
    docker compose build --no-cache
    print_status "Imágenes construidas ✓"
}

# Iniciar servicios
start_services() {
    print_status "Iniciando servicios..."
    docker compose up -d
    print_status "Servicios iniciados ✓"
}

# Verificar estado de servicios
check_services() {
    print_status "Verificando estado de servicios..."
    sleep 5
    
    # Verificar que los contenedores están corriendo
    if [ $(docker compose ps -q | wc -l) -eq 3 ]; then
        print_status "Todos los servicios están corriendo ✓"
    else
        print_error "Algunos servicios no están corriendo"
        docker compose ps
        exit 1
    fi
    
    # Verificar que la API responde
    print_status "Verificando API..."
    sleep 10
    
    if curl -f -s http://localhost:5050/api/health > /dev/null; then
        print_status "API está respondiendo ✓"
    else
        print_warning "API no está respondiendo, verificando logs..."
        docker compose logs app
    fi
}

# Mostrar logs
show_logs() {
    print_status "Mostrando logs de todos los servicios..."
    docker compose logs -f
}

# Detener servicios
stop_services() {
    print_status "Deteniendo servicios..."
    docker compose down
    print_status "Servicios detenidos ✓"
}

# Limpiar todo
clean_all() {
    print_status "Limpiando contenedores, imágenes y volúmenes..."
    docker compose down -v --rmi all
    print_status "Limpieza completada ✓"
}

# Función principal
main() {
    case "${1:-start}" in
        "start")
            check_dependencies
            check_env_file
            build_images
            start_services
            check_services
            print_status "Despliegue completado. API disponible en http://localhost:5050"
            print_status "Para ver logs en tiempo real: ./deploy.sh logs"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            main start
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            clean_all
            ;;
        "status")
            docker compose ps
            ;;
        "build")
            check_dependencies
            check_env_file
            build_images
            ;;
        *)
            echo "Uso: $0 {start|stop|restart|logs|clean|status|build}"
            echo ""
            echo "Comandos:"
            echo "  start   - Construir e iniciar todos los servicios"
            echo "  stop    - Detener todos los servicios"
            echo "  restart - Reiniciar todos los servicios"
            echo "  logs    - Mostrar logs en tiempo real"
            echo "  clean   - Limpiar contenedores, imágenes y volúmenes"
            echo "  status  - Mostrar estado de servicios"
            echo "  build   - Solo construir las imágenes"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
