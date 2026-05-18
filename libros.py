from flask import Flask, render_template, jsonify, request

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