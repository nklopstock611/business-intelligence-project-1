import os
import csv
import pandas as pd
import plotly.graph_objects as go

from io import StringIO
from django.http import FileResponse
from fastapi import FastAPI, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse

from PredictionModel import Model
import html_contents as hc
from utils import *

app = FastAPI()

# ========= #
# TEMPLATES #
# ========= #

templates = Jinja2Templates(directory="templates")

# ========== #
# CONTROLLER #
# ========== #

@app.get("/")
async def root(request: Request):
   # Devuelve la plantilla index.html
   return templates.TemplateResponse("index.html", {"request": request})

@app.get("/predict-text")
async def predict_from_textarea(input: str):
   # Nombre del archivo CSV que se va a escribir
   filename = 'uploaded/review.csv'
   
   # Abrir el archivo CSV en modo escritura
   with open(filename, 'w', newline='') as file:
      # Crear un objeto writer para escribir en el archivo CSV
      writer = csv.writer(file)
      
      # Si el archivo está vacío, escribir la primera fila
      writer.writerow(['', 'review_id'])

      # Esta línea, además de escribir en el csv, genera un id para cada review qu aumenta cada que entra un nuevo registro
      writer.writerow([file.tell()//len(input), input])

   with open(filename, 'r') as df:
      model = Model()
      predictions = model.make_predictions(df)

      print(predictions)

   return {"prediction": input}

@app.post("/predict-file")
async def predict_from_file(request: Request, file: UploadFile):
    # Leer el archivo CSV en un DataFrame
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode()))

    # Hacer predicciones en los datos CSV usando el modelo de aprendizaje automático
    model = Model()
    predictions = model.make_predictions(df)

    # # Unir el CSV de entrada y las predicciones en un único DataFrame
    results_df = pd.concat([df, predictions], axis=1)

    # # Guardar el DataFrame de resultados en un archivo CSV en la carpeta "assets"
    filename = os.path.join("assets", f"{file.filename}_results.csv")
    results_df.to_csv(filename, index=False)

    # Graficar:
    fig = go.Figure(
        data=[go.Pie(
            labels=results_df['sentimiento'].replace({1: "negativo", 0: "positivo"}).value_counts().index,
            values=results_df['sentimiento'].replace({1: "negativo", 0: "positivo"}).value_counts().values,
        )],
        layout=go.Layout(width=400, height=400),
    )

    fig.update_layout(
        title="Gráfica de Pie: Sentimento de reviews",
        legend_title="Sentimiento",
    )

    plot_div = fig.to_html(full_html=False)
    
    html_content = hc.html_content_pie_graph() % fig.to_json() #.format(plot_div)

    # templates.TemplateResponse("index.html", {"request": request, "predictions": predictions["sentimiento"].replace({1: "negativo", 0: "positivo"})})
    # Devolver el nombre del archivo de resultados como respuesta
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/data/{filename}")
async def get_data(filename: str):
   # Cargar el archivo CSV desde la carpeta "assets"
   filepath = os.path.join("assets", f"{filename}_results.csv")

   # Devolver el archivo como respuesta
   return FileResponse(filepath)
