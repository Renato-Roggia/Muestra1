# Makefile simple para ejecutar el juego
APP = Muestra_3x3.py

run:
	@echo "🚀 Ejecutando el juego..."
	python3 $(APP)

clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

