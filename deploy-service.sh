#!/bin/bash
set -e

SERVICE_NAME="flagmodel-embedder"
SERVICE_FILE="${SERVICE_NAME}.service"
INSTALL_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

case "$1" in
    install)
        echo "Installing ${SERVICE_NAME} service..."
        sudo cp "${SERVICE_FILE}" "${INSTALL_PATH}"
        sudo systemctl daemon-reload
        sudo systemctl enable "${SERVICE_NAME}"
        echo "Service installed and enabled!"
        echo ""
        echo "Start the service with: sudo systemctl start ${SERVICE_NAME}"
        echo "Check status with: sudo systemctl status ${SERVICE_NAME}"
        ;;

    start)
        echo "Starting ${SERVICE_NAME}..."
        sudo systemctl start "${SERVICE_NAME}"
        ;;

    stop)
        echo "Stopping ${SERVICE_NAME}..."
        sudo systemctl stop "${SERVICE_NAME}"
        ;;

    restart)
        echo "Restarting ${SERVICE_NAME}..."
        sudo systemctl restart "${SERVICE_NAME}"
        ;;

    status)
        sudo systemctl status "${SERVICE_NAME}"
        ;;

    logs)
        sudo journalctl -u "${SERVICE_NAME}" -f
        ;;

    uninstall)
        echo "Uninstalling ${SERVICE_NAME} service..."
        sudo systemctl stop "${SERVICE_NAME}" 2>/dev/null || true
        sudo systemctl disable "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${INSTALL_PATH}"
        sudo systemctl daemon-reload
        echo "Service uninstalled!"
        ;;

    *)
        echo "Usage: $0 {install|start|stop|restart|status|logs|uninstall}"
        exit 1
        ;;
esac
