# API que expone un modelo de Análisis y Clasificación de Sentimiento de Reviews de Películas.

Antes de ejecutar la API, se deben instalar las librerías usadas. Esto se puede hacer corriendo la siguiente línea en una consola:
```bash
pip install -r requirements.txt
```

Luego, hay que revisar rutas. Si en la primera corrida no funciona, en los archivos "main.py" y "PredictionModel.py" cambien la siguiente línea:
```bash
parent = os.path.dirname(os.path.dirname(os.path.dirname(current)))
```
por:
```bash
parent = os.path.dirname(os.path.dirname(current))
```
