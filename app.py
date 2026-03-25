import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Dashboard CDI", layout="wide")

st.title("🚦 Market Heatmap")

# --- LÓGICA DE DATOS ---
def obtener_metricas_yfinance(ticker, nombre):
    try:
        # Descargamos 1 año de datos para tener la SMA200
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if data.empty:
            return None
        
        # Precio actual (último cierre)
        # Precio actual (usando .iloc[-1] y asegurando que sea escalar)
        precio_actual = float(data['Close'].iloc[-1])
        
        # Cálculos de Medias (añadimos float() para evitar el error de Series)
        sma5 = float(data['Close'].rolling(window=5).mean().iloc[-1])
        ema8 = float(data['Close'].ewm(span=8, adjust=False).mean().iloc[-1])
        ema21 = float(data['Close'].ewm(span=21, adjust=False).mean().iloc[-1])
        sma50 = float(data['Close'].rolling(window=50).mean().iloc[-1])
        sma200 = float(data['Close'].rolling(window=200).mean().iloc[-1])

        return {
            "Ticker": ticker,
            "Nombre": nombre,
            "Precio": precio_actual,
            "vs. DMA5": ((precio_actual / sma5) - 1) * 100,
            "vs. EMA8": ((precio_actual / ema8) - 1) * 100,
            "vs. EMA21": ((precio_actual / ema21) - 1) * 100,
            "vs. SMA50": ((precio_actual / sma50) - 1) * 100,
            "vs. SMA200": ((precio_actual / sma200) - 1) * 100
        }
    except Exception as e:
        return None

# --- ESTILOS DE COLOR ---
def color_semaforo(val):
    try:
        # Forzamos a que val sea un número flotante simple
        v = float(val)
    except (ValueError, TypeError):
        return '' # Si no es un número, no aplicamos color

    if v >= 0.5: color = '#55A43E' # Verde oscuro
    elif v >= 0.26 and v < 0.5: color = '#28A04F' 
    elif v >= 0 and v <= 0.25 : color = '#F1B505' 
    elif v >= -0.25 and v <= 0 : color = "#E66E20" 
    else: color = '#DB3737' 
    return f'background-color: {color}; color: white'

# --- GRUPOS DE ACTIVOS ---
biblioteca = {
    "4 ETF's Principales": {'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones', 'IWM': 'Russell 2000'},
    "Sectores del S&P 500": {'XLY': 'Consumo Básico', 'XLP': 'Consumo Disfrutable', 'XLE': 'Energía', 'XLF': 'Finanzas', 'XLV': 'Salud', 'XLI': 'Industriales', 'XLB': 'Materiales', 'XLK': 'Tecnología', 'XLU': 'Servicios Públicos'},
    "Commodities & FX": {'GC': 'Oro', 'CL': 'Petróleo', 'JPY': 'Yen Japonés', 'BTC-USD': 'Bitcoin'},
    "Magníficas": {'AAPL': 'Apple', 'MSFT': 'Microsoft', 'NVDA': 'Nvidia', 'TSLA': 'Tesla', 'GOOGL': 'Alphabet', 'META': 'Meta', 'AMZN': 'Amazon'},
    
}

# --- RENDERIZADO ---
for seccion, activos in biblioteca.items():
    st.subheader(seccion)
    lista_resultados = []
    
    with st.spinner(f'Consultando {seccion}...'):
        for ticker, nombre in activos.items():
            res = obtener_metricas_yfinance(ticker, nombre)
            if res:
                lista_resultados.append(res)
    
    if lista_resultados:
        df = pd.DataFrame(lista_resultados)
        
        # Aplicar estilos
        cols_metricas = ['vs. DMA5', 'vs. EMA8', 'vs. EMA21', 'vs. SMA50', 'vs. SMA200']
        st.dataframe(
            df.style.map(color_semaforo, subset=cols_metricas)
            .format("{:.2f}%", subset=cols_metricas)
            .format("${:.2f}", subset=['Precio']),
            width="stretch"
        )
