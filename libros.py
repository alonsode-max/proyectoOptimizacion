import os
import random
import pandas as pd

# =====================================================================
# TRUCO DE GEOLOCALIZACIÓN AUTOMÁTICA (Evita el FileNotFoundError)
# =====================================================================
# 1. Obtenemos la ruta real de la carpeta donde vive este archivo "libros.py"
CARPETA_DEL_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# 2. Creamos la ruta perfecta al archivo "libros.csv" combinando la carpeta con el nombre
RUTA_CSV_AUTOMATICA = os.path.join(CARPETA_DEL_SCRIPT, "libros.csv")


class Biblioteca:
    """
    Clase que gestiona la base de datos de "La Morada del Libro"
    utilizando Programación Orientada a Objetos (POO) y la librería Pandas.
    """

    def __init__(self, ruta_csv=RUTA_CSV_AUTOMATICA):
        """
        Constructor de la clase. Se activa automáticamente al hacer: biblioteca = Biblioteca()
        Establece la ruta del archivo de forma inteligente y carga los datos.
        """
        self.ruta_csv = ruta_csv
        self.df = None  # Aquí guardaremos nuestra tabla de datos en memoria (DataFrame)
        self.cargar_datos()

    # =====================================================================
    # ● LECTURA DEL CSV CON PANDAS (Obligatorio)
    # =====================================================================
    def cargar_datos(self):
        """
        Método obligatorio de lectura. Abre el archivo CSV utilizando Pandas.
        Si faltan columnas estadísticas clave (precio, notas, favoritos...),
        Pandas las crea de forma automática para asegurar que todo funcione.
        """
        print(f"📖 Buscando y cargando libros desde la ruta real:\n   ➔ {self.ruta_csv}\n")
        
        # Verificamos si el archivo existe realmente en la carpeta calculada
        if not os.path.exists(self.ruta_csv):
            # En caso de emergencia, si el archivo no existe, creamos uno básico
            columnas = ['id', 'Titulo', 'ISBN', 'Autor', 'Sinopsis', 'Genero', 'Editorial', 'Numero de paginas', 'Serie', 'fecha de publicación']
            self.df = pd.DataFrame(columns=columnas)
            self.guardar_datos()
        else:
            # LECTURA CON PANDAS: cargamos el CSV completo en memoria
            self.df = pd.read_csv(self.ruta_csv)
            
            # Aseguramos que el ID exista y sea numérico entero
            if 'id' in self.df.columns:
                self.df['id'] = pd.to_numeric(self.df['id'], errors='coerce').fillna(0).astype(int)
            else:
                # Si tu CSV no tiene columna de ID, Pandas la inserta al principio
                self.df.insert(0, 'id', range(1, len(self.df) + 1))
                self.guardar_datos()

        # PREPARACIÓN DE LAS COLUMNAS PARA TUS ESTADÍSTICAS OBLIGATORIAS
        # Si vuestro archivo CSV original no tiene estos datos, Pandas los genera de forma lógica
        guardar_cambios = False

        if 'Precio' not in self.df.columns:
            # Generamos precios lógicos calculando 0.02€ por página más un mínimo de 4.99€
            self.df['Precio'] = (self.df['Numero de paginas'] * 0.02 + 4.99).round(2)
            guardar_cambios = True

        if 'Estado' not in self.df.columns:
            # Algunos libros marcados como prestados, la mayoría disponibles
            self.df['Estado'] = random.choices(['Disponible', 'Prestado'], weights=[80, 20], k=len(self.df))
            guardar_cambios = True

        if 'Puntuacion' not in self.df.columns:
            # Notas al azar de 3.0 a 5.0 estrellas para poder calcular los promedios
            self.df['Puntuacion'] = [round(random.uniform(3.0, 5.0), 1) for _ in range(len(self.df))]
            guardar_cambios = True

        if 'Favorito' not in self.df.columns:
            # Marcamos algunos favoritos iniciales ('Si' o 'No')
            self.df['Favorito'] = random.choices(['Si', 'No'], weights=[15, 85], k=len(self.df))
            guardar_cambios = True

        if 'Ventas' not in self.df.columns:
            # Unidades vendidas/alquiladas del libro para poder calcular las ventas totales
            self.df['Ventas'] = [random.randint(5, 100) for _ in range(len(self.df))]
            guardar_cambios = True

        # Si Pandas ha tenido que autogenerar alguna columna, guardamos el CSV finalizado
        if guardar_cambios:
            self.guardar_datos()

        print("✅ Base de datos cargada y optimizada con éxito.\n")

    # =====================================================================
    # ● ESCRITURA DEL CSV CON PANDAS (Obligatorio)
    # =====================================================================
    def guardar_datos(self):
        """
        Método obligatorio de escritura. Guarda los datos que tenemos en la memoria
        de vuelta al archivo CSV original de forma física.
        """
        # ESCRITURA CON PANDAS:
        # index=False evita que Pandas guarde una columna extra con números de fila
        self.df.to_csv(self.ruta_csv, index=False)


    # =====================================================================
    # ● CÁLCULOS ESTADÍSTICOS UTILIZANDO PANDAS (Retornos etiquetados)
    # =====================================================================

    # 1. Total de registros
    def obtener_total_registros(self):
        # Cuenta la cantidad de filas en la tabla actual
        total = int(self.df.shape[0])
        return {"total_registros": total}

    # 2. Promedio de precios
    def obtener_promedio_precios(self):
        # Calcula la media aritmética de la columna de precios usando .mean()
        promedio = float(self.df['Precio'].mean())
        return {"promedio_precios": round(promedio, 2)}

    # 3. Elemento más caro
    def obtener_elemento_mas_caro(self):
        if self.df.empty:
            return {"elemento_mas_caro": "Ninguno"}
        # .idxmax() localiza directamente la fila que contiene el precio más alto
        idx_max = self.df['Precio'].idxmax()
        titulo_caro = self.df.loc[idx_max, 'Titulo']
        precio_caro = float(self.df.loc[idx_max, 'Precio'])
        return {"elemento_mas_caro": f"{titulo_caro} ({precio_caro}€)"}

    # 4. Categoría más utilizada (Género literario)
    def obtener_categoria_mas_utilizada(self):
        if self.df.empty or 'Genero' not in self.df.columns:
            return {"categoria_mas_utilizada": "Ninguna"}
        # Calculamos la "Moda" (el género que más se repite en la columna)
        genero_top = str(self.df['Genero'].mode()[0])
        return {"categoria_mas_utilizada": genero_top}

    # 5. Cantidad de favoritos
    def obtener_cantidad_favoritos(self):
        # Filtramos la tabla dejando solo las filas donde Favorito sea igual a 'Si'
        favoritos = self.df[self.df['Favorito'].str.lower() == 'si']
        cantidad = int(favoritos.shape[0])
        return {"cantidad_favoritos": cantidad}

    # 6. Promedio de puntuaciones
    def obtener_promedio_puntuaciones(self):
        # Calcula la media de puntuación de todos tus libros
        promedio = float(self.df['Puntuacion'].mean())
        return {"promedio_puntuaciones": round(promedio, 2)}

    # 7. Top 5 elementos (Los 5 mejores puntuados)
    def obtener_top_5_elementos(self):
        if self.df.empty:
            return {"top_5_elementos": []}
        # Ordenamos la tabla de mayor a menor puntuación (.sort_values) y tomamos las 5 primeras (.head)
        top_df = self.df.sort_values(by='Puntuacion', ascending=False).head(5)
        lista_top = top_df[['Titulo', 'Puntuacion']].to_dict(orient='records')
        return {"top_5_elementos": lista_top}

    # 8. Total de ventas (Dinero total recaudado)
    def obtener_total_ventas(self):
        # Multiplica fila a fila (Precio * Unidades Vendidas) y luego suma el total de todas con .sum()
        ventas_totales = float((self.df['Precio'] * self.df['Ventas']).sum())
        return {"total_ventas": round(ventas_totales, 2)}


# =====================================================================
#  PRUEBA AUTOMÁTICA EN TU TERMINAL
# =====================================================================
if __name__ == "__main__":
    # Inicializa tu clase apuntando automáticamente a la ruta correcta
    biblioteca = Biblioteca()
    
    print("==============================================")
    print("📈 ESTADÍSTICAS CALCULADAS - LA MORADA DEL LIBRO")
    print("==============================================")
    print(f"1. Total Registros:       {biblioteca.obtener_total_registros()}")
    print(f"2. Promedio de Precios:   {biblioteca.obtener_promedio_precios()}")
    print(f"3. Libro Más Caro:        {biblioteca.obtener_elemento_mas_caro()}")
    print(f"4. Género Más Usado:      {biblioteca.obtener_categoria_mas_utilizada()}")
    print(f"5. Total Favoritos:       {biblioteca.obtener_cantidad_favoritos()}")
    print(f"6. Promedio Puntuación:   {biblioteca.obtener_promedio_puntuaciones()}")
    print(f"7. Total Recaudado:       {biblioteca.obtener_total_ventas()}")
    
    print("\n🏆 TOP 5 DE JOYAS LITERARIAS MEJOR VALORADAS:")
    top_libros = biblioteca.obtener_top_5_elementos()["top_5_elementos"]
    for pos, libro in enumerate(top_libros, 1):
        print(f"   [{pos}] {libro['Titulo']} - Puntuación: {libro['Puntuacion']}★")
    print("==============================================\n")