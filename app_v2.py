import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report

# Título de la aplicación
st.title("Clasificación de Candidatos con Random Forest 🌳")

# ---------------------------
# Carga y visualización de datos
# ---------------------------
st.header("Datos de Entrada")
candidates = {
    'exi': [780,750,690,710,780,730,690,720,740,690,610,690,710,680,770,610,580,650,540,590,620,600,550,550,570,670,660,580,650,760,640,620,660,660,680,650,670,580,590,790],
    'psi': [4,3.9,3.3,3.7,3.9,3.7,2.3,3.3,3.3,1.7,2.7,3.7,3.7,3.3,3.3,3,2.7,3.7,2.7,2.3,3.3,2,2.3,2.7,3,3.3,3.7,2.3,3.7,3.3,3,2.7,4,3.3,3.3,2.3,2.7,3.3,1.7,3.7],
    'experiencia_laboral': [3,4,3,5,4,6,1,4,5,1,3,5,6,4,3,1,4,6,2,3,2,1,4,1,2,6,4,2,6,5,1,2,4,6,5,1,2,1,4,5],
    'edad': [25,28,24,27,26,31,24,25,28,23,25,27,30,28,26,23,29,31,26,26,25,24,28,23,25,29,28,26,30,30,23,24,27,29,28,22,23,24,28,31],
    'admitido': [2,2,1,2,2,2,0,2,2,0,0,2,2,1,2,0,0,1,0,0,1,0,0,0,0,1,1,0,1,2,0,0,1,1,1,0,0,0,0,2]
}
df = pd.DataFrame(candidates, columns=['exi', 'psi', 'experiencia_laboral', 'edad', 'admitido'])
st.write(df)

# ---------------------------
# Preparación de datos y entrenamiento del modelo
# ---------------------------
st.header("Entrenamiento del Modelo")
X = df[['exi', 'psi', 'experiencia_laboral', 'edad']]
y = df['admitido']

# División de datos: 75% entrenamiento y 25% prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

# Entrenar el clasificador Random Forest
clf = RandomForestClassifier(random_state=0)
clf.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
y_pred = clf.predict(X_test)

# ---------------------------
# Evaluación del modelo
# ---------------------------
st.subheader("Evaluación del Modelo")

# Reporte de clasificación y accuracy
rep = classification_report(y_test, y_pred)
acc = metrics.accuracy_score(y_test, y_pred)
st.text("Reporte de Clasificación:")
st.text(rep)
st.write("Accuracy:", acc)

# Matriz de confusión con Plotly
st.text("Matriz de Confusión:")
conf_matrix = pd.crosstab(y_test, y_pred, rownames=['Actual'], colnames=['Predicted'])
class_labels = ["No admitido", "En lista de espera", "Admitido"]
fig = px.imshow(conf_matrix,
                labels=dict(x="Predicted", y="Actual", color="Count"),
                x=class_labels,
                y=class_labels,
                color_continuous_scale="Viridis")
fig.update_xaxes(side="top")
st.plotly_chart(fig)

# Importancia de las características con Altair
st.text("Importancia de las Características:")
feature_labels = ['exi', 'psi', 'experiencia_laboral', 'edad']
feature_importances = pd.Series(clf.feature_importances_, index=feature_labels).sort_values(ascending=False)
fi_df = pd.DataFrame({
    'Feature': feature_importances.index,
    'Importance': feature_importances.values
})
chart = alt.Chart(fi_df).mark_bar().encode(
    x=alt.X('Importance:Q', title='Importancia'),
    y=alt.Y('Feature:N', sort='-x', title='Características'),
    color=alt.Color('Feature:N', legend=None),
    tooltip=['Feature', 'Importance']
).properties(
    title='Importancia de las Características',
    width=600,
    height=300
)
st.altair_chart(chart)

# ---------------------------
# Sección interactiva para predicción
# ---------------------------
st.header("Realiza una Predicción")
exi_input = st.slider("Calificación Examen de Ingreso:", 0, 1000, 500, step=10)
psi_input = st.slider("Puntaje Psicofísico:", 0, 100, 30, step=1)
experiencia_input = st.slider("Experiencia Laboral:", 0, 10, 5, step=1)
edad_input = st.slider("Edad:", 0, 100, 40, step=1)

if st.button("Realizar Predicción"):
    prediction = clf.predict([[exi_input, psi_input, experiencia_input, edad_input]])[0]
    if prediction == 2:
        resultado = "Candidato admitido"
    elif prediction == 1:
        resultado = "Candidato en lista de espera"
    elif prediction == 0:
        resultado = "Candidato no admitido o rechazado"
    else:
        resultado = "Resultado no reconocido"
    st.write("El modelo predice:", resultado)

# ---------------------------
# Cálculo del Impacto Económico
# ---------------------------
st.header("Cálculo del Impacto Económico")
# Convertir la matriz de confusión a NumPy
cm = conf_matrix.values

# Ejemplo: valores económicos asignados a cada clase en caso de predicción correcta
economic_values_correct = np.array([500, 1000, 1500])  # Valores asignados a: [No admitido, En lista de espera, Admitido]
penalty_incorrect = -300  # Penalización por cada predicción equivocada

# Cálculo:
# Suma del valor económico de las predicciones correctas (la diagonal de la matriz)
diag = np.diag(cm)
correcto = np.dot(diag, economic_values_correct)
# Número total de predicciones incorrectas
equivocadas = cm.sum() - np.trace(cm)
# Impacto económico total
impacto = correcto + equivocadas * penalty_incorrect

st.write(f"Impacto Económico Total: ${impacto:,.2f}")
