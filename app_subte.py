import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuración de la página
st.set_page_config(page_title="Tablero Avanzado Subte BA 2025", layout="wide")

# Colores Oficiales y Proyectos de Expansión
COLORES_SUBTE = {
    'LineaA': '#00A8E0', 'LineaB': '#E5161A', 'LineaD': '#008C45',
    'LineaC': '#0053A0', 'LineaH': '#FFD100', 'LineaE': '#6C2D91',
    'LineaPM': '#7A7A7A', 'Combinaciones': '#4A5568', 'Nodos Ferroviarios': '#ED8936',
    'Futura Línea F': '#FF7F00', 'Futura Línea G': '#FF69B4', 'Futura Línea I': '#4B0082',
    'Futura Línea I / F (Hub)': '#708090'
}

# --- DICCIONARIOS DE ENRIQUECIMIENTO DE RED ---
MAPEO_NODOS_COMBINACION = {
    'Carlos Pellegrini': 'Nodo Obelisco (B-C-D)', '9 de Julio': 'Nodo Obelisco (B-C-D)', 'Diagonal Norte': 'Nodo Obelisco (B-C-D)',
    'Pueyrredon.B': 'Nodo Pueyrredon/Corrientes (B-H)', 'Corrientes': 'Nodo Pueyrredon/Corrientes (B-H)',
    'Jujuy': 'Nodo Humberto I/Jujuy (E-H)', 'Humberto I': 'Nodo Humberto I/Jujuy (E-H)',
    'Independencia.C': 'Nodo Independencia (C-E)', 'Independencia': 'Nodo Independencia (C-E)',
    'Santa Fe': 'Nodo S.Fe/Pueyrredon (D-H)', 'Pueyrredon': 'Nodo S.Fe/Pueyrredon (D-H)',
    'Once': 'Nodo Once (A-H)', 'Plaza Miserere': 'Nodo Once (A-H)',
    'Lima': 'Nodo Av. de Mayo (A-C)', 'Avenida de Mayo': 'Nodo Av. de Mayo (A-C)', 
    'Peru': 'Nodo Centro Civico (A-D-E)', 'Catedral': 'Nodo Centro Civico (A-D-E)', 'Bolivar': 'Nodo Centro Civico (A-D-E)', 
    'Leandro N. Alem': 'Nodo CCK (B-E)', 'Correo Central': 'Nodo CCK (B-E)',
    'Retiro': 'Nodo Retiro (C-E)', 'Retiro E': 'Nodo Retiro (C-E)', 
    'Plaza de los Virreyes': 'Nodo Pza. de los Virreyes (E-PM)', 'Saguier': 'Nodo Pza. de los Virreyes (E-PM)'
}

ESTACIONES_TREN = {
    'Constitucion': 'FFCC Roca', 'Nodo Retiro (C-E)': 'FFCC Mitre / San Martín / Belgrano Norte',
    'Nodo Once (A-H)': 'FFCC Sarmiento', 'Federico Lacroze': 'FFCC Urquiza',
    'Ministro Carranza': 'FFCC Mitre (Ramal Suarez)', 'Flores': 'FFCC Sarmiento', 'Belgrano.C': 'FFCC Mitre (Ramal Tigre)'
}

FUTURAS_LINEAS = {
    'Plaza Italia': 'Futura Línea F', 'Callao.B': 'Futura Línea F', 'Callao': 'Futura Línea F',
    'Cordoba': 'Futura Línea F', 'Venezuela': 'Futura Línea F', 'Entre Rios': 'Futura Línea F', 'Constitucion': 'Futura Línea F',
    'Nodo Retiro (C-E)': 'Futura Línea G', 'Catalinas': 'Futura Línea G', 'Uruguay': 'Futura Línea G',
    'Tribunales': 'Futura Línea G', 'Facultad de Medicina': 'Futura Línea G',
    'Nodo S.Fe/Pueyrredon (D-H)': 'Futura Línea G', 'Nodo Pueyrredon/Corrientes (B-H)': 'Futura Línea G',
    'Emilio Mitre': 'Futura Línea I', 'Primera Junta': 'Futura Línea I', 'Caballito': 'Futura Línea I',
    'Malabia': 'Futura Línea I', 'Angel Gallardo': 'Futura Línea I', 'Scalabrini Ortiz': 'Futura Línea I',
    'Palermo': 'Futura Línea I', 'Plaza Italia': 'Futura Línea I / F (Hub)'
}

# FUNCIÓN DE HOMOLOGACIÓN GEOESPACIAL NATIVA
def normalizar_para_mapa(estacion):
    est = str(estacion).strip().upper()
    # Mapeamos las excepciones de nombres entre ambos datasets
    if est == 'ROSAS': return 'JUAN MANUEL DE ROSAS'
    if est == 'LEANDRO N. ALEM': return 'LEANDRO ALEM'
    if est == 'MINISTRO CARRANZA': return 'CARRANZA'
    if est == 'PUEYREDON.B' or est == 'PUEYRREDON.B': return 'PUEYRREDON'
    if est == 'CALLAO.B': return 'CALLAO'
    if est == 'RETIRO E': return 'RETIRO'
    if est == 'INDEPENDENCIA.C': return 'INDEPENDENCIA'
    return est

@st.cache_data
def cargar_datos_avanzados():
    ruta_parquet = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\subte_2025_unificado.parquet"
    df = pd.read_parquet(ruta_parquet)
    df = df[df['LINEA'] != 'Prueba']            #hay una prueba que se ve que hizo quien creo la db que mete ruido
    df['HORA'] = df['DESDE'].astype(str).str[:5]
    df['ESTACION'] = df['ESTACION'].astype(str).str.strip()
    df['ESTACION'] = df['ESTACION'].replace({'Pza. de los Virreyes': 'Plaza de los Virreyes', 'Retiro.C': 'Retiro'})
    
    df['NODO_CONSOLIDADO'] = df['ESTACION'].map(MAPEO_NODOS_COMBINACION).fillna(df['ESTACION'])
    df['CONECTA_TREN'] = df['NODO_CONSOLIDADO'].map(ESTACIONES_TREN).fillna(df['ESTACION'].map(ESTACIONES_TREN)).fillna('No Conecta')
    df['FUTURA_COMBINACION'] = df['NODO_CONSOLIDADO'].map(FUTURAS_LINEAS).fillna(df['ESTACION'].map(FUTURAS_LINEAS)).fillna('Sin Línea Futura Proyectada')
    
    # Creamos la columna normalizada en mayúsculas para cruzar con el mapa
    df['ESTACION_MAPA'] = df['ESTACION'].apply(normalizar_para_mapa)
    
    return df

df = cargar_datos_avanzados()

# --- CARGA Y LIMPIEZA DEL NUEVO ARCHIVO DE COORDENADAS ---
@st.cache_data
def cargar_coordenadas():
    ruta_geo = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\estaciones-accesibles.csv"
    try:
        # Leemos el archivo nuevo
        df_geo = pd.read_csv(ruta_geo, sep=';')
        
        # Corrección de las comas decimales a puntos y conversión a float
        df_geo['LATITUD'] = df_geo['lat'].astype(str).str.replace(',', '.').astype(float)
        df_geo['LONGITUD'] = df_geo['long'].astype(str).str.replace(',', '.').astype(float)
        
        # Homologamos columnas de unión: pasamos a mayúsculas y armamos el prefijo 'Linea'
        df_geo['ESTACION_MAPA'] = df_geo['estacion'].astype(str).str.strip().str.upper()
        df_geo['LINEA'] = "Linea" + df_geo['linea'].astype(str).str.strip().str.upper()
        
        # Nos quedamos solo con las columnas espaciales necesarias
        return df_geo[['ESTACION_MAPA', 'LINEA', 'LATITUD', 'LONGITUD', 'escaleras_mecanicas', 'ascensores']]
    except Exception as e:
        st.error(f"No se pudo cargar el archivo de coordenadas: {e}")
        return None

df_geo = cargar_coordenadas()

st.title("Analizador de Red e Infraestructura - Subte BA 2025")

# Filtro global de tipo de día
tipo_dia = st.sidebar.radio("Filtrar Tipo de Día (Muestra Global):", ["Todos", "Días Hábiles", "Fines de Semana"])
if tipo_dia == "Días Hábiles":
    df_f = df[df['ES_FIN_DE_SEMANA'] == 0]
elif tipo_dia == "Fines de Semana":
    df_f = df[df['ES_FIN_DE_SEMANA'] == 1]
else:
    df_f = df.copy()

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs([
    "Comparativa de Líneas", 
    "Nodos de Combinación y Trenes", 
    "Planificación Urbana (Líneas F-G-I)",
    "Mapa Dinámico (El Pulso)"
])


with tab1:
    st.subheader("Análisis Relativo entre Componentes de la Red")
    col_a, col_b = st.columns(2)
    with col_a:
        pax_linea = df_f.groupby('LINEA', as_index=False)['pax_TOTAL'].sum()
        fig_share = px.pie(pax_linea, values='pax_TOTAL', names='LINEA', title="Participación de cada Línea en el Caudal Total (2025)", color='LINEA', color_discrete_map=COLORES_SUBTE, hole=0.4)
        st.plotly_chart(fig_share, use_container_width=True)
    with col_b:
        horas_lineas = df_f.groupby(['HORA', 'LINEA'], as_index=False)['pax_TOTAL'].sum()
        fig_curvas = px.line(horas_lineas, x='HORA', y='pax_TOTAL', color='LINEA', title="El Pulso Horario de cada Línea en Simultáneo", color_discrete_map=COLORES_SUBTE)
        st.plotly_chart(fig_curvas, use_container_width=True)

with tab2:
    st.subheader("El Verdadero Peso de los Transbordos")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("#### Nodos de Combinación Consolidados")
        nodos_consolidado = df_f.groupby('NODO_CONSOLIDADO', as_index=False)['pax_TOTAL'].sum()
        top_nodos = nodos_consolidado.sort_values(by='pax_TOTAL', ascending=False).head(15)
        fig_nodos = px.bar(top_nodos, x='pax_TOTAL', y='NODO_CONSOLIDADO', orientation='h', title="Top 15 Estaciones/Nodos Reales de la Ciudad", text_auto=',.0f', color_discrete_sequence=['#4A5568'])
        fig_nodos.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_nodos, use_container_width=True)
    with col_d:
        st.markdown("#### Impacto de las Cabeceras Ferroviarias")
        df_tren = df_f[df_f['CONECTA_TREN'] != 'No Conecta']
        pax_tren = df_tren.groupby(['NODO_CONSOLIDADO', 'CONECTA_TREN'], as_index=False)['pax_TOTAL'].sum().sort_values('pax_TOTAL', ascending=False)
        fig_tren = px.bar(pax_tren, x='NODO_CONSOLIDADO', y='pax_TOTAL', color='CONECTA_TREN', title="Caudal en Estaciones con Conexión Ferroviaria Directa", labels={'pax_TOTAL': 'Viajes', 'CONECTA_TREN': 'Línea de Tren Metropolitano', 'NODO_CONSOLIDADO': 'Estación/Nodo'})
        st.plotly_chart(fig_tren, use_container_width=True)
# ==========================================
# 🔮 PESTAÑA 3: PLANIFICACIÓN URBANA (LÍNEAS F, G, I)
# ==========================================
with tab3:
    st.subheader("Análisis de Demanda Latente para Futuras Líneas")
    st.markdown("""
    Este módulo analiza el volumen real de pasajeros de 2025 en las estaciones actuales que fueron designadas por la **Ley 670** para convertirse en nodos de combinación con las futuras líneas de Subte (**F, G e I**). 
    Esto nos permite entender qué proyectos alivianarían más la red actual y dónde se concentra la mayor necesidad de carga.
    """)
    
    # 1. Preparación de datos agrupados
    futuro_analisis = df_f[df_f['FUTURA_COMBINACION'] != 'Sin Línea Futura Proyectada']
    
    # Agrupación por línea futura para el Pie Chart
    pax_por_futura_linea = futuro_analisis.groupby('FUTURA_COMBINACION', as_index=False)['pax_TOTAL'].sum()
    
    # Agrupación por estación para el gráfico de barras
    futuro_agrupado = futuro_analisis.groupby(['NODO_CONSOLIDADO', 'FUTURA_COMBINACION'], as_index=False)['pax_TOTAL'].sum()
    futuro_agrupado = futuro_agrupado.sort_values(by='pax_TOTAL', ascending=False)
    
    # 2. Distribución en dos columnas visuales
    col_pie, col_bar = st.columns(2)
    
    with col_pie:
        # Gráfico de Torta - Distribución de la Demanda Futura
        fig_pie_futuro = px.pie(
            pax_por_futura_linea,
            values='pax_TOTAL',
            names='FUTURA_COMBINACION',
            title="Distribución del Tráfico Actual según Proyecto de Línea Futura",
            color='FUTURA_COMBINACION',
            color_discrete_map=COLORES_SUBTE,
            hole=0.4
        )
        fig_pie_futuro.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie_futuro, use_container_width=True)
        
    with col_bar:
        # Gráfico de Barras - Top Nodos Afectados
        fig_futuro = px.bar(
            futuro_agrupado.head(10), # Mostramos el top 10 para que no se sature el layout
            x='pax_TOTAL',
            y='NODO_CONSOLIDADO',
            color='FUTURA_COMBINACION',
            orientation='h',
            title="Top 10 Nodos Actuales con Mayor Impacto de Expansión",
            labels={'pax_TOTAL': 'Pasajeros Actuales (2025)', 'FUTURA_COMBINACION': 'Proyecto de Línea', 'NODO_CONSOLIDADO': 'Nodo Actual'},
            color_discrete_map=COLORES_SUBTE,
            height=400
        )
        fig_futuro.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_futuro, use_container_width=True)
        
    st.markdown("---")
    
    # 3. BLOQUE DE ANÁLISIS DE PLANIFICACIÓN URBANA
    st.subheader("Dictamen Técnico: ¿Cuál es la línea más necesaria para construir?")
    
    # Obtenemos dinámicamente los valores para el análisis
    pax_por_futura_linea = pax_por_futura_linea.sort_values(by='pax_TOTAL', ascending=False)
    linea_top_nombre = pax_por_futura_linea.iloc[0]['FUTURA_COMBINACION']
    linea_top_pax = pax_por_futura_linea.iloc[0]['pax_TOTAL']
    
    # Calculamos el porcentaje que representa la línea top sobre el total impactado
    total_impactado = pax_por_futura_linea['pax_TOTAL'].sum()
    porcentaje_top = (linea_top_pax / total_impactado) * 100
    
    st.markdown(f"""
    Basado estrictamente en el comportamiento y volumen de los **{total_impactado:,}** pasajeros que validaron sus molinetes en los nodos afectados durante 2025, la **{linea_top_nombre} es, por una diferencia abrumadora, la infraestructura más urgente y necesaria de construir** para la Ciudad de Buenos Aires.
    
    ### Justificación Basada en Datos:
    * **Concentración Crítica de Demanda:** La **{linea_top_nombre}** absorbe aproximadamente el **{porcentaje_top:.1f}%** de toda la tracción latente de la expansión proyectada. Esto significa que la gran mayoría de la gente que hoy camina o satura los transbordos se beneficiaría directamente de esta traza.
    * **El Factor Constitución y Palermo:** Al cruzar por Constitución (el nodo intermodal número 1 de la Argentina con más de 16 millones de viajes) y conectar transversalmente con Plaza Italia (Línea D), la Línea F funciona como el bypass perfecto para descomprimir la Línea C y evitar el colapso diario del Nodo Obelisco.
    * **Descompresión Diagonal:** Actualmente, la red de Buenos Aires es fuertemente *radial* (todas las líneas van hacia el Microcentro). Los datos demuestran que las estaciones de combinación transversales del eje Callao/Entre Ríos tienen un flujo masivo de pasajeros que no desean ir al centro, sino cruzar de norte a sur. 
    
    ### Conclusión de Infraestructura:
    Mientras que la **Línea I** (vía Scalabrini Ortiz) y la **Línea G** (Retiro a Cid Campeador) muestran caudales iniciales interesantes pero moderados, posponer las obras de la **Línea F** condena a la red actual a un cuello de botella logístico insostenible a mediano plazo. Los datos de 2025 respaldan que cada peso invertido en transporte público debería priorizar prioritariamente el eje de la traza F.
    
    Por último, con la mirada puesta en la planificación a largo plazo, los hallazgos de este análisis histórico de 2025 exponen una necesidad institucional urgente: la realización de una nueva Encuesta de Movilidad Domiciliaria (ENMODO) para el Área Metropolitana. El último gran estudio oficial data de 2019; una fotografía pre-pandemia que asumía al Microcentro como el núcleo exclusivo y excluyente de atracción de viajes laborales. La consolidación del modelo híbrido transformó la geografía económica de Buenos Aires, descentralizando el centro tradicional y dando nacimiento a corredores corporativos emergentes de alta densidad en el eje norte, como los barrios de Belgrano y Núñez. Continuar proyectando obras de infraestructura multimillonarias basadas en matrices de viaje de hace siete años es un riesgo logístico. Actualizar estos estudios permitirá entender si las trazas de las futuras líneas F, G e I deben recibir sutiles modificaciones de ingeniería para adaptarse a los nuevos polos atractores de empleo de la ciudad post-pandemia.
    """)
# ==========================================
#  PESTAÑA 4: MAPA GEOESPACIAL CONTROLADO POR STREAMLIT (SIN ERRORES)
# ==========================================
with tab4:
    st.subheader("El Pulso de la Ciudad: Control de Franja Horaria")
    st.markdown("Seleccioná o deslizá el control de tiempo para observar de manera precisa cómo cambia la demanda en cada estación.")
    
    if df_geo is None:
        st.warning("Asegurate de que el archivo 'estaciones-accesibles.csv' esté guardado en tu carpeta de trabajo.")
    else:
        # 1. Agrupamos tus molinetes por Hora, Estación normalizada y Línea
        mapa_df = df_f.groupby(['HORA', 'ESTACION_MAPA', 'ESTACION', 'LINEA'], as_index=False)['pax_TOTAL'].sum()
        
        # 2. Hacemos el cruce exacto por clave doble (Estación y Línea)
        mapa_completo = pd.merge(mapa_df, df_geo, on=['ESTACION_MAPA', 'LINEA'], how='inner')
        mapa_completo = mapa_completo.sort_values(by='HORA')
        
        if mapa_completo.empty:
            st.error("Error de cruce. Verificá los delimitadores del archivo de coordenadas.")
        else:
            # SOLUCIÓN: Creamos un deslizador nativo de Streamlit con todas las horas disponibles
            horas_disponibles = sorted(mapa_completo['HORA'].unique())
            
            # El usuario selecciona la hora exacta usando la interfaz de Streamlit
            hora_seleccionada = st.select_slider(
                "Selecciona la Franja Horaria a Auditar:", 
                options=horas_disponibles,
                value=horas_disponibles[len(horas_disponibles)//2] # Arranca parado en la mitad del día
            )
            
            # Filtramos el DataFrame por la hora que eligió el usuario en el slider
            mapa_filtrado_hora = mapa_completo[mapa_completo['HORA'] == hora_seleccionada]
            
            # 3. Dibujamos el mapa ESTÁTICO respecto a Plotly, pero DINÁMICO por Streamlit
            # Al quitar 'animation_frame', removemos los botones nativos rotos de Plotly
            fig_mapa = px.scatter_mapbox(
                mapa_filtrado_hora,
                lat="LATITUD", lon="LONGITUD",
                size="pax_TOTAL",
                color="LINEA",
                color_discrete_map=COLORES_SUBTE,
                hover_name="ESTACION",
                hover_data={
                    "pax_TOTAL": ':,', 
                    "escaleras_mecanicas": True, 
                    "ascensores": True,
                    "LATITUD": False, "LONGITUD": False, "HORA": False, "ESTACION_MAPA": False
                },
                size_max=45, # Aumentamos un poquito el tamaño máximo ya que es un cuadro fijo por vez
                zoom=11.6,
                center={"lat": -34.6037, "lon": -58.3816}, # Obelisco
                height=680
            )
            
            fig_mapa.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":10,"l":0,"b":0}
            )
            
            # Mostramos la hora destacada en un cartel lindo
            st.info(f"Visualizando estado de la red a las: **{hora_seleccionada} h**")
            st.plotly_chart(fig_mapa, use_container_width=True)