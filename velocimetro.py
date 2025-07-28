import dash
from dash import html
import plotly.graph_objects as go

app = dash.Dash(__name__)

# Simular humedad actual
humedad_actual = 72  # porcentaje

# Crear gráfico tipo gauge
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=humedad_actual,
    title={'text': "Humedad (%)"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#38b000"},
        'steps': [
            {'range': [0, 30], 'color': '#e3f2fd'},
            {'range': [30, 70], 'color': '#90ee90'},
            {'range': [70, 100], 'color': '#ffcccb'}
        ]
    }
))

# Mostrar en página
app.layout = html.Div([
    html.H2("Velocímetro de Humedad", style={'textAlign': 'center'}),
    html.Div([
        html.Div(dash.dcc.Graph(figure=fig))
    ])
])

if __name__ == '__main__':
    app.run(debug=True)

