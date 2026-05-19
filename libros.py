from flask import Flask, render_template, jsonify, request, Response
import os
import pandas as pd
from typing import List, Dict, Any, Optional

CARPETA_DEL_SCRIPT: str = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV: str = os.path.join(CARPETA_DEL_SCRIPT, "libros.csv")


class Biblioteca:
    def __init__(self, ruta_csv: str = RUTA_CSV) -> None:
        """Inicializa la ruta, la lista de favoritos y carga los datos."""
        self.ruta_csv: str = ruta_csv
        self.df: pd.DataFrame = pd.DataFrame()
        self.favoritos: List[int] = []
        self.cargar_datos()

    def cargar_datos(self) -> None:
        """Lee el CSV, limpia conflictos, normaliza columnas y valida tipos."""
        if not os.path.exists(self.ruta_csv):
            raise FileNotFoundError(f"¡Error! No se encuentra el archivo en: {self.ruta_csv}")

        try:
            with open(self.ruta_csv, 'r', encoding='utf-8', errors='ignore') as f:
                lineas: List[str] = f.readlines()
            
            lineas_limpias: List[str] = [
                l for l in lineas 
                if not any(marca in l for marca in ['<<<<<<<', '=======', '>>>>>>>'])
            ]
            
            if len(lineas_limpias) < len(lineas):
                with open(self.ruta_csv, 'w', encoding='utf-8') as f:
                    f.writelines(lineas_limpias)
                print("🧹 [Autolimpieza] Se eliminaron marcas de conflicto en 'libros.csv'.")
        except Exception as e:
            print(f"⚠️ Nota de seguridad al escanear el CSV: {e}")

        self.df = pd.read_csv(self.ruta_csv)
        self.df.columns = self.df.columns.str.strip()
        
        mapeo_columnas: Dict[str, str] = {
            'id': 'id',
            'titulo': 'Titulo',
            'isbn': 'ISBN',
            'autor': 'Autor',
            'sinopsis': 'Sinopsis',
            'genero': 'Genero',
            'editorial': 'Editorial',
            'numero de paginas': 'Numero_pag',
            'serie': 'Serie',
            'fecha': 'Fecha',
            'precio': 'Precio',
            'puntuacion': 'Puntuacion'
        }
        self.df.rename(columns=lambda x: mapeo_columnas.get(x.lower(), x), inplace=True)
        
        if 'id' not in self.df.columns:
            self.df['id'] = range(1, len(self.df) + 1)
            self.guardar_datos()

        self.df['id'] = pd.to_numeric(self.df['id'], errors='coerce').fillna(0).astype(int)
        
        for col in ['Precio', 'Puntuacion']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0.0)
                
        if 'Numero_pag' in self.df.columns:
            self.df['Numero_pag'] = pd.to_numeric(self.df['Numero_pag'], errors='coerce').fillna(0).astype(int)

    def guardar_datos(self) -> None:
        """Guarda los datos en memoria de vuelta en el archivo CSV."""
        self.df.to_csv(self.ruta_csv, index=False)

    def agregar_favorito(self, libro_id: int) -> None:
        """Añade un ID a la lista de favoritos."""
        if libro_id not in self.favoritos:
            self.favoritos.append(libro_id)

    def eliminar_favorito(self, libro_id: int) -> None:
        """Retira un ID de la lista de favoritos."""
        if libro_id in self.favoritos:
            self.favoritos.remove(libro_id)

    def obtener_libro(self, libro_id: int) -> Any:
        """Busca un libro por ID y lo devuelve limpio o None si no existe."""
        fila: pd.DataFrame = self.df[self.df['id'] == libro_id]
        if fila.empty:
            return None
        return fila.fillna("").to_dict(orient='records')[0]

    def crear_libro_db(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un ID consecutivo, añade el libro al DataFrame y guarda."""
        nuevo_id: int = int(self.df['id'].max() + 1) if not self.df.empty else 1
        datos['id'] = nuevo_id
        
        if 'Precio' in datos:
            datos['Precio'] = pd.to_numeric(datos['Precio'], errors='coerce')
        if 'Puntuacion' in datos:
            datos['Puntuacion'] = pd.to_numeric(datos['Puntuacion'], errors='coerce')
        if 'Numero_pag' in datos:
            datos['Numero_pag'] = pd.to_numeric(datos['Numero_pag'], errors='coerce')

        nuevo_df: pd.DataFrame = pd.DataFrame([datos])
        self.df = pd.concat([self.df, nuevo_df], ignore_index=True)
        self.guardar_datos()
        return datos

    def eliminar_libro_db(self, libro_id: int) -> bool:
        """Elimina el libro del DataFrame y limpia favoritos."""
        if libro_id in self.df['id'].values:
            self.df = self.df[self.df['id'] != libro_id]
            self.eliminar_favorito(libro_id)
            self.guardar_datos()
            return True
        return False


    def consultar_libros(self, filtros: Dict[str, Any], orden: Optional[str]) -> List[Dict[str, Any]]:
        #Aplica filtros y criterios de ordenamiento en cadena sobre el DataFrame.
        df_filtrado = self.df.copy()

        # 1. Filtros en cascada
        if filtros.get('nombre'):
            df_filtrado = df_filtrado[df_filtrado['Titulo'].str.contains(filtros['nombre'], case=False, na=False)]
        
        if filtros.get('precio_max') is not None:
            df_filtrado = df_filtrado[df_filtrado['Precio'] <= filtros['precio_max']]
            
        if filtros.get('fecha'):
            df_filtrado = df_filtrado[df_filtrado['Fecha'].astype(str).str.contains(filtros['fecha'], na=False)]
            
        if filtros.get('genero'):
            df_filtrado = df_filtrado[df_filtrado['Genero'].str.contains(filtros['genero'], case=False, na=False)]
            
        if filtros.get('favorito') is True:
            df_filtrado = df_filtrado[df_filtrado['id'].isin(self.favoritos)]

        # 2. Ordenamiento lógico eficiente
        if orden:
            mapeo_orden = {
                "alfa_asc": ("Titulo", True),
                "alfa_desc": ("Titulo", False),
                "precio_asc": ("Precio", True),
                "precio_desc": ("Precio", False),
                "paginas_asc": ("Numero_pag", True),
                "paginas_desc": ("Numero_pag", False),
                "reciente": ("Fecha", False)
            }
            if orden in mapeo_orden:
                columna, ascendente = mapeo_orden[orden]
                df_filtrado = df_filtrado.sort_values(by=columna, ascending=ascendente)

        return df_filtrado.fillna("").to_dict(orient='records')

    def obtener_total_registros(self) -> int:
        return int(self.df.shape[0])

    def obtener_promedio_precios(self) -> float:
        if 'Precio' not in self.df.columns or self.df.empty:
            return 0.0
        return round(float(self.df['Precio'].mean()), 2)

    def obtener_elemento_mas_caro(self) -> str:
        if self.df.empty or 'Precio' not in self.df.columns:
            return "Ninguno"
        idx_max = self.df['Precio'].idxmax()
        return f"{self.df.loc[idx_max, 'Titulo']} ({float(self.df.loc[idx_max, 'Precio'])}€)"

    def obtener_categoria_mas_utilizada(self) -> str:
        if self.df.empty or 'Genero' not in self.df.columns:
            return "Ninguna"
        return str(self.df['Genero'].mode()[0])

    def obtener_cantidad_favoritos(self) -> int:
        return len(self.favoritos)

    def obtener_top_5_mas_caros(self) -> List[Dict[str, Any]]:
        if self.df.empty or 'Precio' not in self.df.columns:
            return []
        top_df: pd.DataFrame = self.df.sort_values(by='Precio', ascending=False).head(5)
        return top_df[['Titulo', 'Precio']].to_dict(orient='records')


app = Flask(__name__)

biblioteca: Any = None
try:
    biblioteca = Biblioteca()
except FileNotFoundError as e:
    print(e)


@app.before_request
def verificar_biblioteca() -> Any:
    #Interceptor centralizado para evitar comprobaciones redundantes en las rutas.
    if request.endpoint != 'inicio' and biblioteca is None:
        return jsonify({"error": "Base de datos no inicializada"})
    return None


@app.route("/")
def inicio() -> str:
    return render_template("libro.html")

@app.route("/ver-libro")
def ver_libro() -> str:
    return render_template("libro.html")


@app.route("/guardar", methods=["POST"])
def guardar() -> Response:
    biblioteca.guardar_datos()
    return jsonify({"mensaje": "Datos guardados correctamente en el CSV"})


@app.route("/libros", methods=["GET"])
def enviar_todos_los_libros() -> Response: 
    #Parámetros Query

    '''COMO HACER UNA PETICION:
    Buscar por nombre: /libros?nombre=Quijote

    Filtrar por precio máximo: /libros?precio_max=25.50

    Filtrar por género: /libros?genero=Fantasía

    Filtrar por favoritos: /libros?favorito=true

    Filtrar por fecha: /libros?fecha=2023

    Criterios de Ordenamiento (?orden=)

    Ascendente alfabéticamente: /libros?orden=alfa_asc

    Descendente alfabéticamente: /libros?orden=alfa_desc

    Mayor a menor precio: /libros?orden=precio_desc

    Menor a mayor precio: /libros?orden=precio_asc

    Mayor a menor cantidad páginas: /libros?orden=paginas_desc

    Menor a mayor cantidad páginas: /libros?orden=paginas_asc

    Más reciente: /libros?orden=reciente

    Ejemplo de súper consulta combinada:
    /libros?genero=Fantasía&precio_max=30&orden=paginas_desc
'''
    filtros = {
        'nombre': request.args.get('nombre'),
        'precio_max': request.args.get('precio_max', type=float),
        'fecha': request.args.get('fecha'),
        'genero': request.args.get('genero'),
        'favorito': request.args.get('favorito', default='false').lower() == 'true'
    }
    orden = request.args.get('orden')

    lista_libros = biblioteca.consultar_libros(filtros, orden)

    estadisticas: Dict[str, Any] = {
        "total": biblioteca.obtener_total_registros(),
        "promedio_precio": biblioteca.obtener_promedio_precios(),
        "mas_caro": biblioteca.obtener_elemento_mas_caro(),
        "categoria_mas_utilizada": biblioteca.obtener_categoria_mas_utilizada(),
        "cantidad_favoritos": biblioteca.obtener_cantidad_favoritos(),
        "top_5_mas_caros": biblioteca.obtener_top_5_mas_caros()
    }
    
    return jsonify({
        "libros": lista_libros,
        "estadisticas": estadisticas
    })


@app.route("/libro/<int:libro_id>", methods=["GET"])
def enviar_un_libro(libro_id: int) -> Any:
    libro: Any = biblioteca.obtener_libro(libro_id)
    if libro:
        if libro_id in biblioteca.favoritos:
            libro['Favorito']=True
        return jsonify(libro)
    return jsonify({"error": f"Libro con ID {libro_id} no encontrado"}), 404


@app.route("/modifFav/<int:libro_id>", methods=["PUT"])
def modificar_favorito(libro_id: int) -> Any:
    if libro_id in biblioteca.df['id'].values:
        if libro_id in biblioteca.favoritos:
            biblioteca.eliminar_favorito(libro_id)
            return jsonify({
                "mensaje": f"Libro eliminado de favoritos con éxito",
                "cantidad_favoritos": biblioteca.obtener_cantidad_favoritos()
            })
        else:
            biblioteca.agregar_favorito(libro_id)
            return jsonify({
                "mensaje": f"Libro añadido a favoritos con éxito",
                "cantidad_favoritos": biblioteca.obtener_cantidad_favoritos()
            })
    return jsonify({"error": "El libro que intentas marcar no existe en el catálogo"}), 404


@app.route("/eliminarLibro/<int:libro_id>", methods=["DELETE"])
def eliminar_libro(libro_id: int) -> Any:
    if biblioteca.eliminar_libro_db(libro_id):
        return jsonify({"mensaje": f"Libro eliminado correctamente"})
    return jsonify({"error": f"No se encontró el libro"}), 404


@app.route("/libro", methods=["POST"])
def añadir_libro() -> Any:
    datos: Any = request.get_json()
    if not datos or 'Titulo' not in datos:
        return jsonify({"error": "Faltan datos obligatorios. El campo 'Titulo' es obligatorio."}), 400
    
    nuevo_libro: Dict[str, Any] = biblioteca.crear_libro_db(datos)
    return jsonify({
        "mensaje": "Libro creado y añadido correctamente",
        "libro": nuevo_libro
    }), 201


if __name__ == "__main__":
    app.run()