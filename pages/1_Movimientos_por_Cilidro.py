import streamlit as st
import mysql.connector
import pandas as pd
import os
from auth import check_password

# 1) Validación de contraseña
if not check_password():
    st.stop()

# 2) Función de conexión y carga desde Cloud SQL via Cloud Run
def get_sql_data(query: str) -> pd.DataFrame:
    # Leemos las variables de entorno que cargamos en Cloud Run
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")

    # Conexión usando el Cloud SQL Proxy (unix_socket)
    conn = mysql.connector.connect(
        user=db_user,
        password=db_pass,
        database=db_name,
        unix_socket=f"/cloudsql/{instance_connection_name}"
    )
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 3) Ejecutar queries para cargar los datasets
df_proceso = get_sql_data("SELECT * FROM PROCESO;")
df_detalle = get_sql_data("SELECT * FROM DETALLE;")

# 4) Normalizar columna SERIE (igual que antes)
df_detalle["SERIE"] = df_detalle["SERIE"].astype(str).str.replace(",", "", regex=False)

# 5) UI (idéntica)
st.title("FASTRACK")
st.subheader("CONSULTA DE MOVIMIENTOS POR CILINDRO")

target_cylinder = st.text_input("Ingrese la ID del cilindro a buscar:")

if st.button("Buscar"):
    if target_cylinder:
        target_cylinder_normalized = target_cylinder.replace(",", "")
        df_det_for_cyl = df_detalle.loc[
            df_detalle["SERIE"] == target_cylinder_normalized,
            ["IDPROC", "SERIE", "SERVICIO"]
        ]

        df_proc_for_cyl = df_proceso[
            df_proceso["IDPROC"].isin(df_det_for_cyl["IDPROC"])
        ]

        if df_proc_for_cyl.empty:
            st.warning("No se encontraron movimientos para el cilindro ingresado.")
        else:
            df_resultados = df_proc_for_cyl.merge(
                df_det_for_cyl,
                on="IDPROC",
                how="left"
            )

            st.success(f"Movimientos para el cilindro ID {target_cylinder}:")
            st.dataframe(
                df_resultados[
                    ["FECHA", "HORA", "IDPROC", "PROCESO", "CLIENTE", "UBICACION", "SERIE", "SERVICIO"]
                ]
            )

            def convert_to_csv(dataframe: pd.DataFrame) -> bytes:
                return dataframe.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Descargar resultados en CSV",
                data=convert_to_csv(df_resultados),
                file_name=f"movimientos_{target_cylinder}.csv",
                mime="text/csv",
            )
    else:
        st.warning("Por favor, ingrese una ID de cilindro.")
