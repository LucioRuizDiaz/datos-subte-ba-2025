import pandas as pd

def analizar_datos_subte():
    ruta_parquet = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\subte_2025_unificado.parquet"
    
    print("🚀 Cargando el dataset unificado (Formato Parquet)...")
    df = pd.read_parquet(ruta_parquet)
    
    total_pasajeros = df['pax_TOTAL'].sum()
    print(f"📊 Total de viajes registrados en el período: {total_pasajeros:,}\n")
    
    # 1. TOP 10 ESTACIONES
    print("🔝 TOP 10 ESTACIONES MÁS TRANSITADAS EN 2025:")
    top_estaciones = df.groupby('ESTACION')['pax_TOTAL'].sum().sort_values(ascending=False).head(10)
    for i, (estacion, pax) in enumerate(top_estaciones.items(), 1):
        porcentaje = (pax / total_pasajeros) * 100
        print(f"  {i}. {estacion:<25} -> {pax:>12,} viajes ({porcentaje:.2f}%)")
        
    # 2. VIAJES POR LÍNEA
    print("\n🚇 VOLUMEN DE PASAJEROS POR LÍNEA:")
    por_linea = df.groupby('LINEA')['pax_TOTAL'].sum().sort_values(ascending=False)
    for linea, pax in por_linea.items():
        porcentaje = (pax / total_pasajeros) * 100
        print(f"  - {linea:<15} -> {pax:>12,} viajes ({porcentaje:.2f}%)")
        
    # 3. DÍAS HÁBILES VS FIN DE SEMANA
    print("\n📅 DINÁMICA: DÍAS HÁBILES VS FIN DE SEMANA:")
    por_tipo_dia = df.groupby('ES_FIN_DE_SEMANA')['pax_TOTAL'].sum()
    # Calculamos promedios diarios reales para comparar bien
    dias_habiles = df[df['ES_FIN_DE_SEMANA'] == 0]['FECHA'].nunique()
    dias_finde = df[df['ES_FIN_DE_SEMANA'] == 1]['FECHA'].nunique()
    
    pax_habil_prom = por_tipo_dia.get(0, 0) / dias_habiles if dias_habiles > 0 else 0
    pax_finde_prom = por_tipo_dia.get(1, 0) / dias_finde if dias_finde > 0 else 0
    
    print(f"  - Promedio diario en Días Hábiles:   {int(pax_habil_prom):,} pasajeros.")
    print(f"  - Promedio diario en Fines de Semana: {int(pax_finde_prom):,} pasajeros.")

if __name__ == "__main__":
    analizar_datos_subte()