import os
import io
import pandas as pd

def unificar_datos():
    ruta_carpeta = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\molinetes-2025"
    ruta_salida_csv = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\subte_2025_unificado.csv"
    ruta_salida_parquet = r"C:\Users\lucio\OneDrive\Desktop\COSAS\subte\subte_2025_unificado.parquet"

    # Listar los archivos descargados
    archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith('.csv') and 'PAX15min' in f]

    if not archivos:
        print(f"No se encontraron archivos en: {ruta_carpeta}")
        return

    print(f"Se encontraron {len(archivos)} archivos para procesar.")
    columnas_interes = ['FECHA', 'LINEA', 'ESTACION', 'DESDE', 'pax_TOTAL']
    lista_dataframes = []

    for i, archivo in enumerate(archivos, 1):
        ruta_completa_archivo = os.path.join(ruta_carpeta, archivo)
        print(f"[{i}/{len(archivos)}] Procesando: {archivo}...")

        # cp1252 es el encoding estándar de Windows-Sudamérica, ideal para la 'ñ' y tildes
        for encod in ['cp1252', 'latin-1', 'utf-8']:
            try:
                # 1. Leemos el archivo completo como texto plano para limpiar las comillas externas de raíz
                with open(ruta_completa_archivo, 'r', encoding=encod) as f:
                    lineas_limpias = [linea.replace('"', '').strip() for linea in f]
                
                # Unimos las líneas limpias en un solo bloque de texto
                texto_limpio = "\n".join(lineas_limpias)
                
                # 2. Le pasamos el texto limpio a Pandas simulando que es un archivo usando StringIO
                df_temporal = pd.read_csv(io.StringIO(texto_limpio), sep=';')
                
                # Limpieza de espacios extras en las cabeceras por las dudas
                df_temporal.columns = df_temporal.columns.str.strip()
                
                # 3. Filtramos las columnas que nos importan
                df_temporal = df_temporal[columnas_interes]
                
                # Limpieza básica de strings en los campos de texto
                df_temporal['ESTACION'] = df_temporal['ESTACION'].astype(str).str.strip()
                df_temporal['LINEA'] = df_temporal['LINEA'].astype(str).str.strip()
                
                # 4. Agrupamos y consolidamos para ahorrar memoria RAM
                df_agrupado = df_temporal.groupby(['FECHA', 'LINEA', 'ESTACION', 'DESDE'], as_index=False)['pax_TOTAL'].sum()
                lista_dataframes.append(df_agrupado)
                break # Si procesó con éxito, salimos del bucle de encodings e ídem al siguiente archivo
                
            except Exception as e:
                ultimo_error = e
                continue
        else:
            print(f"❌ Error crítico al procesar {archivo}: {ultimo_error}")

    if not lista_dataframes:
        print("❌ No se pudo consolidar ninguna tabla. Revisar delimitadores.")
        return

    # Combina todos los DataFrames mensuales en una única tabla unificada
    print("\nCombinando todos los fragmentos logrados...")
    df_final = pd.concat(lista_dataframes, ignore_index=True)

    # Conversión de fechas segura
    print("Formateando fechas y extrayendo variables temporales...")
    df_final['FECHA'] = pd.to_datetime(df_final['FECHA'], format='%d/%m/%Y', errors='coerce')
    df_final = df_final.dropna(subset=['FECHA'])

    # Ingeniería de variables temporales para tus visualizaciones
    df_final['MES'] = df_final['FECHA'].dt.month
    df_final['DIA_SEMANA'] = df_final['FECHA'].dt.dayofweek
    df_final['ES_FIN_DE_SEMANA'] = df_final['DIA_SEMANA'].isin([5, 6]).astype(int)
    
    dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    df_final['NOMBRE_DIA'] = df_final['DIA_SEMANA'].map(dias_es)

    # Guardar resultados finales
    print(f"\n💾 Guardando CSV unificado en: {ruta_salida_csv}")
    df_final.to_csv(ruta_salida_csv, index=False, sep=';', encoding='utf-8')
    
    print(f"💾 Guardando copia Parquet en: {ruta_salida_parquet}")
    df_final.to_parquet(ruta_salida_parquet, index=False)
    
    print(f"\n¡Éxito total! Filas unificadas finales: {len(df_final):,}")

if __name__ == "__main__":
    unificar_datos()