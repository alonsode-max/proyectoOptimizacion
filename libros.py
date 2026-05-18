from flask import Flask, render_template, jsonify, request
import os
import pandas as pd

CARPETA_DEL_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(CARPETA_DEL_SCRIPT, "libros.csv")


class Biblioteca:
    """
    Clase que gestiona la base de datos de "La Morada del Libro"
    utilizando Programación Orientada a Objetos (POO) y la librería Pandas.
    """

    def __init__(self, ruta_csv=RUTA_CSV):
        """
        Constructor de la clase. Inicializa la ruta, carga los datos del CSV
        y crea la lista de favoritos vacía en memoria.
        """
        self.ruta_csv = ruta_csv
        self.df = None  # DataFrame de Pandas donde se almacena la información
        
        self.favoritos = []
        
        self.cargar_datos()

    def cargar_datos(self):
        """
        Lee el archivo CSV directamente usando Pandas.
        Convierte los tipos de datos de vuestras columnas para asegurar
        que las operaciones matemáticas funcionen perfectamente.
        """
        if not os.path.exists(self.ruta_csv):
            raise FileNotFoundError(f"¡Error! No se encuentra el archivo en: {self.ruta_csv}")

        try:
            with open(self.ruta_csv, 'r', encoding='utf-8', errors='ignore') as f:
                lineas = f.readlines()
            
            # Filtramos cualquier línea de conflicto de Git que se haya colado
            lineas_limpias = [
                l for l in lineas 
                if not any(marca in l for marca in ['<<<<<<<', '=======', '>>>>>>>'])
            ]
            
            # Si detectamos marcas, reescribimos el archivo limpio de forma inmediata
            if len(lineas_limpias) < len(lineas):
                with open(self.ruta_csv, 'w', encoding='utf-8') as f:
                    f.writelines(lineas_limpias)
                print("🧹 [Autolimpieza] Se eliminaron marcas de conflicto en 'libros.csv'.")
        except Exception as e:
            print(f"⚠️ Nota de seguridad al escanear el CSV: {e}")

        # LECTURA CON PANDAS
        self.df = pd.read_csv(self.ruta_csv)
        
        # LIMPIEZA DE COLUMNAS: Quitamos espacios en blanco al inicio y final de los nombres de columnas
        self.df.columns = self.df.columns.str.strip()
        
        # Corregimos de forma automática si alguna columna clave está en minúsculas
        mapeo_columnas = {
            'titulo': 'Titulo',
            'isbn': 'ISBN',
            'autor': 'Autor',
            'sinopsis': 'Sinopsis',
            'genero': 'Genero',
            'editorial': 'Editorial',
            'numero de paginas': 'Numero de paginas',
            'serie': 'Serie',
            'fecha de publicacion': 'fecha de publicación',
            'precio': 'Precio',
            'estado': 'Estado',
            'puntuacion': 'Puntuacion',
            'favorito': 'Favorito'
        }
        # Renombramos las columnas si coincide alguna en minúscula
        self.df.rename(columns=lambda x: mapeo_columnas.get(x.lower(), x), inplace=True)
        
        # Formateo y limpieza de tipos de datos de vuestras columnas reales
        if 'id' in self.df.columns:
            self.df['id'] = pd.to_numeric(self.df['id'], errors='coerce').fillna(0).astype(int)
        
        if 'Precio' in self.df.columns:
            self.df['Precio'] = pd.to_numeric(self.df['Precio'], errors='coerce').fillna(0.0)
        
        if 'Puntuacion' in self.df.columns:
            self.df['Puntuacion'] = pd.to_numeric(self.df['Puntuacion'], errors='coerce').fillna(0.0)

    def guardar_datos(self):
        """
        Guarda los datos que están en memoria de vuelta en vuestro archivo libros.csv.
        """
        self.df.to_csv(self.ruta_csv, index=False)


    def agregar_favorito(self, libro_id):
        """
        Añade el ID de un libro a la lista de favoritos si no está ya guardado.
        Esta función se llamará automáticamente cuando pulsen el botón en la web.
        """
        id_num = int(libro_id)
        if id_num not in self.favoritos:
            self.favoritos.append(id_num)

    def eliminar_favorito(self, libro_id):
        """
        Retira el ID de un libro de la lista de favoritos.
        Esta función se llamará automáticamente cuando desmarquen el botón en la web.
        """
        id_num = int(libro_id)
        if id_num in self.favoritos:
            self.favoritos.remove(id_num)


    # =====================================================================
    # ● CÁLCULOS ESTADÍSTICOS EXIGIDOS (Usando Pandas)
    # =====================================================================

    # 1. Total de registros
    def obtener_total_registros(self):
        """Devuelve el número total de libros registrados en el catálogo."""
        total = int(self.df.shape[0])
        return {"total_registros": total}

    # 2. Promedio de precios
    def obtener_promedio_precios(self):
        """Calcula el precio medio de vuestros libros."""
        if 'Precio' not in self.df.columns or self.df.empty:
            return {"promedio_precios": 0.0}
        promedio = float(self.df['Precio'].mean())
        return {"promedio_precios": round(promedio, 2)}

    # 3. Elemento más caro
    def obtener_elemento_mas_caro(self):
        """Busca el libro con el precio más alto en vuestra base de datos."""
        if self.df.empty or 'Precio' not in self.df.columns:
            return {"elemento_mas_caro": "Ninguno"}
        idx_max = self.df['Precio'].idxmax()
        titulo_caro = self.df.loc[idx_max, 'Titulo']
        precio_caro = float(self.df.loc[idx_max, 'Precio'])
        return {"elemento_mas_caro": f"{titulo_caro} ({precio_caro}€)"}

    # 4. Categoría más utilizada (Género literario)
    def obtener_categoria_mas_utilizada(self):
        """Determina cuál es el género más repetido (la moda)."""
        if self.df.empty or 'Genero' not in self.df.columns:
            return {"categoria_mas_utilizada": "Ninguna"}
        genero_top = str(self.df['Genero'].mode()[0])
        return {"categoria_mas_utilizada": genero_top}

    # 5. Cantidad de favoritos (Lista vacía + Conteo tradicional con len)
    def obtener_cantidad_favoritos(self):
        cantidad = len(self.favoritos)
        return cantidad

    # 6. Top 5 elementos más caros
    def obtener_top_5_mas_caros(self):
        """Ordena de mayor a menor precio y extrae los 5 libros más caros."""
        if self.df.empty or 'Precio' not in self.df.columns:
            return {"top_5_mas_caros": []}
        # Ordenamos la tabla de mayor a menor precio y cogemos los 5 primeros
        top_df = self.df.sort_values(by='Precio', ascending=False).head(5)
        lista_top = top_df[['Titulo', 'Precio']].to_dict(orient='records')
        return lista_top


app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/guardar", methods=["POST"])
def guardar():
    return jsonify({"mensaje":"Datos guardados correctamente"})

@app.route("/libros", methods=["GET"])
def enviar_todos_los_libros(): #Incluir estadisticas y mostrar en la pagina principal
    pass

@app.route("/libro/<id>", methods=["GET"])
def enviar_un_libro(id):
    pass

@app.route("/añadirFav/<id>", methods=["PUT"])
def añadir_favorito(id):
    pass

@app.route("/eliminarLibro/<id>", methods=["DELETE"])
def eliminar_libro(id):
    pass

@app.route("/libro", methods=["POST"])
def añadir_libro():
    pass

if __name__ == "__main__":
    try:
        biblioteca = Biblioteca()
        
    except FileNotFoundError as e:
        print(e)