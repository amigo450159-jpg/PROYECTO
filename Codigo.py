import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st  # UI consolidada
from pathlib import Path

#Leer el codigo
url ='https://raw.githubusercontent.com/amigo450159-jpg/PROYECTO/refs/heads/main/base_de_datos.csv'

df=pd.read_csv(url)

#Limpieza
df=df.dropna(axis=1, how= 'all')
df=df.drop(['Codigo DANE', 'Nombre Del Proyecto','Trimestre','Contraprestacion'],axis=1)

#  Renombrar columnas (lista coincide exactamente con las seleccionadas)
df.columns = ["Municipio", "Departamento", "Recurso", "Año","Unidades", "Regalias", "Volumen"]

# Conversión simple: reemplazar comas por puntos, quitar "$" y espacios
df['Regalias'] = (
    df['Regalias']
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
df["Regalias"] = pd.to_numeric(df["Regalias"], errors="coerce")


df['Volumen'] = (
    df['Volumen']
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
df["Volumen"] = pd.to_numeric(df["Volumen"], errors="coerce")

df['Año'] = (df['Año'].astype(str)
.str.replace(",","",regex=False)
             ).str.strip()

#  Convertir tipos (robusto con to_numeric para manejar valores no numéricos)
df["Año"] = pd.to_numeric(df["Año"])


# Normalizar texto
df["Recurso"] = df["Recurso"].astype(str).str.strip()
df["Departamento"] = df["Departamento"].astype(str).str.strip()

#  Frecuencia Recurso x Departamento
counts = (
    df.groupby(["Recurso", "Departamento"]).size().reset_index(name="Frecuencia")
)

#  Frecuencia por Recurso (Top 10)
freq_recursos = (
    df["Recurso"].value_counts().rename_axis("Recurso").reset_index(name="Frecuencia")
)

freq_recursos["Porcentaje"] = (freq_recursos["Frecuencia"] / len(df) * 100).round(2)
freq_recursos_top10 = freq_recursos.head(10)

 #  Gráfico de torta (pie) para Top 10 recursos por frecuencia

total_registros = freq_recursos["Frecuencia"].sum()
top10_pct = freq_recursos_top10.copy()
top10_pct["Porcentaje"] = (top10_pct["Frecuencia"] / total_registros) * 100
plt.figure(figsize=(12, 7))
bars = plt.barh(top10_pct["Recurso"], top10_pct["Porcentaje"], color="#4C78A8")
plt.gca().invert_yaxis()
plt.xlabel("Participación (%)")
plt.title("Participación (%) Top 10 recursos por frecuencia")
for i, v in enumerate(top10_pct["Porcentaje"]):
    plt.text(v + 0.5, i, f"{v:.1f}%", va="center")
plt.tight_layout()
plt.savefig("frecuencia_top10_recursos_barras_pct.png", dpi=150)
plt.close()

#4) Gráfico de barras para Departamento vs Recurso (frecuencia)

dep_totales = counts.groupby("Departamento")["Frecuencia"].sum().sort_values(ascending=False)
rec_totales = counts.groupby("Recurso")["Frecuencia"].sum().sort_values(ascending=False)
top_departamentos_10 = dep_totales.head(10).index
top_recursos_10 = rec_totales.head(10).index

pivot_top10 = counts.pivot(index="Departamento", columns="Recurso", values="Frecuencia").fillna(0)
pivot_top10 = pivot_top10.loc[top_departamentos_10, pivot_top10.columns.intersection(top_recursos_10)]

fig_w = max(10, len(pivot_top10.columns) * 0.8)
fig_h = max(8, len(pivot_top10.index) * 0.6)
plt.figure(figsize=(fig_w, fig_h))
sns.heatmap(pivot_top10, cmap="mako", annot=True, fmt="g", cbar_kws={"label": "Frecuencia"})
plt.title("Frecuencia Top 10 Departamento × Top 10 Recurso")
plt.xlabel("Recurso")
plt.ylabel("Departamento")
plt.tight_layout()
plt.savefig("frecuencia_dep_vs_rec_heatmap_top10.png", dpi=150)
plt.close()

#  Métricas de dispersión simplificadas por recurso 
pivot_full = counts.pivot(index="Departamento", columns="Recurso", values="Frecuencia").fillna(0)
col_totales = pivot_full.sum(axis=0)
active = (pivot_full > 0).sum(axis=0)
media_condicional = pivot_full.mask(pivot_full == 0).mean(axis=0)
top1_share = (pivot_full.max(axis=0) / col_totales.where(col_totales != 0)).fillna(0)

metrics = pd.DataFrame({
    "Departamentos_activos": active,
    "Frecuencia_total": col_totales,
    "Media_condicional": media_condicional,
    "Top1_share": top1_share,
}).sort_values("Frecuencia_total", ascending=False)
metrics.index.name = "Recurso"
metrics_reset = metrics.reset_index()

# Listas de referencia (según imagen de política de gobierno)
lista_estrategicos_canon = [
    "Aluminio", "Caliza", "Carbon Metalúrgico", "Cobre", "Cromo",
    "Esmeraldas", "Fosfato", "Hierro", "Magnesio", "Manganeso",
    "Materiales de construcción", "Níquel", "Oro", "Platino", "Sílice", "Yeso"
]

# Diccionario para unificar diferentes variaciones de nombres de minerales bajo una categoría estándar
map_estrategicos = {
    "Aluminio": ["ALUMINIO"],
    "Caliza": ["CALIZAS", "CALIZA"],
    "Carbon Metalúrgico": ["CARBON METALURGICO"],
    "Cobre": ["COBRE"],
    "Cromo": ["CROMO - CROMITA"],
    "Esmeraldas": [
        "ESMERALDAS", "ESMERALDAS EN BRUTO", "ESMERALDAS TALLADAS",
        "ESMERALDAS ENGASTADA", "ESMERALDAS SEMIPRECIOSA"
    ],
    "Fosfato": ["ROCA FOSFORICA"],
    "Hierro": ["HIERRO"],
    "Magnesio": ["MAGNESIO"],
    "Manganeso": ["MANGANESO"],
    "Materiales de construcción": [
        "GRAVAS", "ARENAS", "ARENA DE RIO", "ARENA DE CANTERA",
        "GRAVAS DE RIO", "GRAVA DE CANTERA", "PIEDRA ARENISCA-PIEDRA BOGOTANA",
        "PUZOLANAS"
    ],
    "Níquel": ["NIQUEL"],
    "Oro": ["ORO"],
    "Platino": ["PLATINO"],
    "Sílice": ["ARENAS SILICEAS"],
    "Yeso": ["YESO"],
}

# Lista de recursos de carbón
lista_carbon = ["CARBON", "CARBON TERMICO", "CARBON ANTRACITA"]

# Función de categorización
def categorize_resource(value: str) -> str:
    r = str(value).strip().upper()
    if r in [x.upper() for x in lista_carbon]:
        return "Carbon"
    for etiquetas in map_estrategicos.values():
        if r in [e.upper() for e in etiquetas]:
            return "Estrategico"
    return "Otros"
# Aplicar categorización al DataFrame
df["Categoria"] = df["Recurso"].apply(categorize_resource)

# Comparativo: Recurso (por categoría) vs Valor de Regalías por Municipio
#Agrupamos **Municipio** Y **Categoría** y Suma todas las regalías de cada combinación
regalias_muni_cat = (
    df.groupby(["Municipio", "Categoria"]) ["Regalias"].sum().reset_index()
)
# Se toma solo los 12 mas grandes municipios por regalías totales
top_munis = (
    regalias_muni_cat.groupby("Municipio")["Regalias"].sum().nlargest(12).index
)
regalias_muni_cat_top = regalias_muni_cat[regalias_muni_cat["Municipio"].isin(top_munis)]

#Creación de gráfico de barras apiladas
plt.figure(figsize=(14, 8))
sns.barplot(
    data=regalias_muni_cat_top,
    x="Municipio",
    y="Regalias",
    hue="Categoria",
    palette={"Estrategico": "#4C78A8", "Carbon": "#F58518", "Otros": "#54A24B"},
)
plt.xticks(rotation=45, ha="right")
plt.title("Regalías por Municipio y Categoría (Top 12 municipios)")
plt.tight_layout()
plt.savefig("regalias_municipio_categoria_top12.png", dpi=150)
plt.close()

# 2) Comparativo: Recursos estratégicos vs Carbón (total país)
regalias_categoria_total = df.groupby("Categoria")["Regalias"].sum().reset_index()

plt.figure(figsize=(8, 5))
sns.barplot(
    data=regalias_categoria_total,
    x="Categoria",
    y="Regalias",
    order=["Estrategico", "Carbon", "Otros"],
    palette={"Estrategico": "#4C78A8", "Carbon": "#F58518", "Otros": "#54A24B"},
)
plt.title("Regalías totales por categoría: Estratégicos vs Carbón vs Otros")
plt.tight_layout()
plt.savefig("regalias_categoria_total.png", dpi=150)
plt.close()


# ------------------ Escritura consolidada en un único Excel  ------------------
with pd.ExcelWriter("analisis_mineria.xlsx") as writer:
    # Hojas principales del análisis
    counts.to_excel(writer, sheet_name="Frecuencia_Rec_Dep", index=False)
    freq_recursos.to_excel(writer, sheet_name="Frecuencia_Recursos", index=False)
    freq_recursos_top10.to_excel(writer, sheet_name="Top10_Recursos", index=False)
    pivot_top10.reset_index().to_excel(writer, sheet_name="Pivot_Top10", index=False)
    metrics_reset.to_excel(writer, sheet_name="Resumen_Dispersion", index=False)

    regalias_muni_cat_top.to_excel(
        writer, sheet_name="Regalias_Muni_Categoria_Top12", index=False
    )
    regalias_categoria_total.to_excel(
        writer, sheet_name="Regalias_Categoria_Total", index=False
    )

print("✅ Excel consolidado generado: analisis_mineria.xlsx (7 hojas)")

# =====================
# STREAMLIT APP 
# =====================
# Estructura simple para ver gráficas generadas y un DataFrame básico.
st.set_page_config(page_title="Análisis Minero", layout="wide")

# ---------- Estilos: reducir espacios y padding ----------
#Streamlit normalmente no permite HTML/CSS por seguridad, pero con unsafe_allow_html=True puedes insertar código HTML/CSS personalizado.
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px;}
    .element-container {margin-bottom: 0.75rem;}
    .stMarkdown {margin-bottom: 0.5rem;}
    .justify {text-align: justify;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Análisis Minero y Transición Energética")
st.caption("Vista consolidada: introducción, objetivos, frecuencias, comparativos y datos básicos")

# Imagen de portada bajo el título
_base_dir = Path(__file__).resolve().parent
_portada_candidates = [Path("portada.png"), _base_dir / "portada.png"]
_portada = next((p for p in _portada_candidates if p.exists()), None)
if _portada is not None:
    st.image(str(_portada), use_container_width=True)
else:
    st.caption("No se encontró el archivo portada.png en el proyecto.")

st.sidebar.title("Navegación")
page = st.sidebar.radio(
    "Secciones",
    (
        "Introducción",
        "Planteamiento del problema",
        "Objetivos",
        "Justificacion",
        "Frecuencias",
        "Comparativos",
        "Datos",
        "Conclusiones",
    ),
)
# Solo UNA página puede estar activa a la vez
# elif garantiza que solo se ejecuta UN bloque
# elif dice claramente: "estas opciones son mutuamente excluyentes"

if page == "Introducción":
    # ---------- Introducción (restaurada) ----------
    st.subheader("Introducción")
    st.markdown(
        """
        <div class='justify'>
        Colombia enfrenta el reto de avanzar hacia una transición energética que reduzca su dependencia de combustibles fósiles y promueva el uso de tecnologías sostenibles. A pesar de los compromisos adquiridos en materia ambiental y climática, el país mantiene un modelo extractivo dominado por el carbón y otros recursos tradicionales. Paralelamente, minerales estratégicos como el níquel, el cobre o el litio —fundamentales para sistemas de almacenamiento energético,
         movilidad eléctrica y energías renovables— no han alcanzado niveles de explotación acordes con las proyecciones de una economía baja en carbono.
        La distribución de las regalías mineras refleja además una marcada desigualdad territorial que limita el desarrollo local, especialmente en zonas donde la actividad extractiva genera impactos ambientales y sociales. En este contexto, el análisis de datos se convierte en una herramienta clave para comprender el comportamiento del sector, identificar tendencias y evaluar si el país avanza de manera coherente con los objetivos de sostenibilidad.
        Este proyecto realiza un análisis detallado de un dataset oficial para examinar la relación entre volúmenes de explotación, tipos de minerales y distribución de regalías. A través de técnicas de exploración, limpieza y visualización, se busca generar conclusiones basadas en evidencia que permitan evaluar el estado actual de la minería frente a la transición energética.
        </div>
        """,
        unsafe_allow_html=True,
    )

elif page == "Objetivos":
    # ---------- Objetivos  ----------
    st.subheader("Objetivos")
    st.write(
        """
        - Visualizar la distribución de recursos (Top 10) y su presencia por departamento.
        - Comparar regalías por categoría (Estratégicos vs Carbón) y por municipio.
        - Proveer una tabla básica del dataset para inspección y validación.
        """
    )
    # ---------- Planteamiento del problema ---------
elif page == "Planteamiento del problema":
    st.subheader("Planteamiento del problema")
    st.markdown(
        """
        <div class='justify'>
        En Colombia, la explotación minera continúa enfocándose principalmente en recursos fósiles como el carbón, a pesar de que el país ha declarado su compromiso con la transición energética y la reducción de emisiones. Esta situación evidencia una desconexión entre el discurso institucional sobre sostenibilidad y las dinámicas reales de producción minera.
        Aunque el Gobierno ha identificado minerales estratégicos —como el níquel, el cobre y el litio— como fundamentales para impulsar tecnologías limpias, su nivel de explotación y su participación en la economía aún son bajos en comparación con los minerales convencionales. Esto genera una brecha entre la intención de avanzar hacia una economía baja en carbono y el estado actual del sector extractivo.
        A este desafío se suma la distribución desigual de las regalías derivadas de la explotación minera. Si bien estas rentas deberían contribuir al desarrollo regional sostenible, en muchos municipios la asignación resulta insuficiente o poco proporcional al volumen de explotación, limitando su capacidad para generar proyectos de impacto y cerrar brechas territoriales.
        Debido a estas condiciones, se vuelve necesario analizar datos reales de explotación minera y regalías para comprender cómo se comportan los diferentes tipos de minerales, qué tendencias predominan y qué tan alineada está la producción del país con los objetivos de la transición energética. A través de la exploración, limpieza, visualización e interpretación de estos datos, es posible identificar patrones relevantes que permitan evaluar si Colombia está avanzando hacia un modelo productivo sostenible o si persisten rezagos que afectan la competitividad y el desarrollo territorial.
        </div>
        """,
        unsafe_allow_html=True,
    )
    # ---------- Justificacion ---------
elif page == "Justificacion":
    st.subheader("Justificacion")
    st.markdown(
        """
        <div class='justify'>
        La transición energética es una prioridad global, y Colombia ha asumido compromisos para reducir su dependencia de recursos fósiles e impulsar el uso de tecnologías limpias. Sin embargo, la permanencia del carbón como principal mineral explotado y la baja participación de minerales estratégicos generan dudas sobre el avance real del país hacia un modelo sostenible.
        Analizar datos reales del sector minero permite:

        -Identificar si existen cambios en la explotación hacia minerales estratégicos.

        -Evaluar la concentración o diversificación productiva.

        -Determinar la distribución de regalías y sus implicaciones territoriales.

        -Proporcionar evidencia para apoyar decisiones de política pública.

        -Comprender si las tendencias actuales respaldan o limitan la transición energética.
        
        Este análisis no solo contribuye al ámbito académico del curso de análisis de datos, sino que también aporta perspectivas relevantes sobre una problemática real del país, fortaleciendo la capacidad de interpretar datos para generar conclusiones significativas.
        </div>
        """,
        unsafe_allow_html=True,
    )
    
 # ---------- Frecuencias ---------
elif page == "Frecuencias":
    st.subheader("Frecuencias")
    st.write("Tablas de frecuencia por recurso y matriz pivot Top10.")
    st.write("Frecuencia por recurso (con porcentaje):")
    st.dataframe(freq_recursos, use_container_width=True, height=360)
    st.write("Matriz Departamento × Recurso (Top10 seleccionados):")
    st.dataframe(pivot_top10, use_container_width=True, height=360)
    cols = st.columns([1, 1], gap="small")
    with cols[0]:
        st.image("frecuencia_top10_recursos_barras_pct.png", caption="Top 10 recursos por frecuencia (%)", use_container_width=True)
        st.caption("Datos obtenidos del portal de Datos Abiertos del Estado Colombiano (datos.gov.co)")
    with cols[1]:
        st.image("frecuencia_dep_vs_rec_heatmap_top10.png", caption="Heatmap Frecuencia: Departamento × Recurso (Top10)", use_container_width=True)
        st.caption("Datos obtenidos del portal de Datos Abiertos del Estado Colombiano (datos.gov.co)")

    # Interpretación en formato limpio-Analisis cualitativo
    st.markdown("Interpretación de las frecuencias:")
    st.markdown(
        """
        - Oro (18.8%), plata (14.1%), gravas y arenas (18%).
        - Carbón + carbón térmico ≈ 10%; aun así concentran las mayores regalías.
        - Los minerales estratégicos (níquel, cobre, etc.) no aparecen en el top de frecuencia.
        """
    )
    st.info("Esto confirma la brecha entre discurso de transición energética y realidad productiva.")

    st.markdown("En la Matriz Departamentos × Recursos:")
    st.markdown(
        """
        - Boyacá, Cundinamarca, Antioquia y Santander concentran diversidad de recursos.
        - El Chocó destaca por oro y platino; no por carbón.
        - La Guajira y el Cesar son centros históricos del carbón.
        """
    )
    st.info("La explotación está territorialmente concentrada en ciertos departamentos.")
 # ---------- Comparativos ---------
elif page == "Comparativos":
    st.subheader("Comparativos: Estratégicos vs Carbón")
    st.write("Regalías totales por categoría y por municipio (Top 12).")
    colA, colB = st.columns([1, 1], gap="small")
    with colA:
        # Formateo de moneda para claridad (COP con separador de miles)
        regalias_categoria_total_fmt = regalias_categoria_total.copy()
        regalias_categoria_total_fmt["Regalias"] = regalias_categoria_total_fmt["Regalias"].map(lambda x: f"$ {x:,.0f}")
        st.dataframe(regalias_categoria_total_fmt, use_container_width=True, height=300)
        st.caption("Montos expresados en pesos colombianos (COP)")
        st.image("regalias_categoria_total.png", caption="Regalías totales por categoría", use_container_width=True)
        st.caption("Datos obtenidos del portal de Datos Abiertos del Estado Colombiano (datos.gov.co)")
    with colB:
        st.write("Regalías por municipio y categoría (Top 12 municipios):")
        regalias_muni_cat_top_fmt = regalias_muni_cat_top.copy()
        regalias_muni_cat_top_fmt["Regalias"] = regalias_muni_cat_top_fmt["Regalias"].map(lambda x: f"$ {x:,.0f}")
        st.dataframe(regalias_muni_cat_top_fmt, use_container_width=True, height=300)
        st.caption("Montos expresados en pesos colombianos (COP)")
        st.image("regalias_municipio_categoria_top12.png", caption="Regalías por municipio y categoría (Top 12)", use_container_width=True)
        st.caption("Datos obtenidos del portal de Datos Abiertos del Estado Colombiano (datos.gov.co)")

    # Interpretación de comparativos -Analisis cualitativo
    st.markdown("Interpretación de regalías por categoría:")
    st.markdown(
        """
        - Carbón: 3.36 cuatrillones COP en regalías (dominante absoluto).
        - Minerales estratégicos: apenas 0.684 cuatrillones.
        - Otros: ~11 cuatrillones, pero suman muchas categorías menores.
        """
    )
    st.info("Conclusión: el carbón domina las regalías, incluso si no domina la frecuencia de explotación.")

    st.markdown("Regalías por municipio:")
    st.markdown(
        """
        - Agustín Codazzi, Barrancas, Albania y municipios de La Guajira y Cesar concentran casi todas las regalías del carbón.
        - Los municipios con minerales estratégicos reciben montos casi simbólicos en comparación → 49,000 COP vs billones del carbón.
        """
    )
    st.info("La desigualdad en regalías es muy marcada entre municipios.")

 # ---------- Datos ---------

elif page == "Datos":
    st.subheader("Datos básicos del dataset")
    columnas_basicas = ["Municipio", "Departamento", "Recurso", "Año", "Regalias", "Volumen"]
    st.write("Vista básica (primeros 200 registros):")
    df_basico = df[columnas_basicas].head(200).copy()
    df_basico["Regalias"] = df_basico["Regalias"].map(lambda x: f"$ {x:,.0f}")
    st.dataframe(df_basico, use_container_width=True, height=380)
    st.caption("Montos expresados en pesos colombianos (COP)")

# ---------- Conclusiones ---------
elif page == "Conclusiones":
    st.subheader("Conclusiones")
    st.markdown(
        """
        <div class='justify'>
        Conclusiones
        
        El análisis de datos evidencia una desconexión clara entre los objetivos de la transición energética en Colombia y la estructura real de explotación minera del país. Aunque el volumen de explotación está diversificado entre recursos como oro, plata, arenas y gravas, los minerales estratégicos —fundamentales para tecnologías limpias— presentan una participación marginal tanto en frecuencia como en generación de regalías.
        
        La información revela que el carbón, pese a no ser el recurso más frecuente, continúa siendo el mineral dominante en términos económicos. Sus regalías superan ampliamente a las de los minerales estratégicos, lo que confirma la dependencia del país de este recurso fósil. Esta concentración económica refuerza un modelo extractivo que aún no se alinea con los objetivos de una economía baja en carbono.
        
        Asimismo, las regalías muestran una distribución territorial desigual. Municipios localizados en el Cesar y La Guajira reciben montos extraordinariamente altos derivados del carbón, mientras que los municipios asociados a minerales estratégicos reciben valores muy bajos en comparación. Esta disparidad limita la capacidad de los territorios productores de minerales emergentes para impulsar su desarrollo regional y fortalecer su infraestructura económica para la transición energética.
        
        En conjunto, los resultados permiten concluir que Colombia aún enfrenta importantes rezagos en la diversificación productiva necesaria para avanzar hacia la transición energética. Aunque existe un discurso institucional orientado a promover minerales estratégicos, su realidad productiva y económica muestra que el país continúa anclado a los combustibles fósiles. El análisis evidencia la necesidad de fortalecer políticas de incentivo, inversión y desarrollo territorial que permitan equilibrar la explotación mineral con las metas nacionales de sostenibilidad.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("analisis realizado por Martha cristina arias rodriguez correo: marthacristinaarias@hotmail.com")
#Fin del codigo😊