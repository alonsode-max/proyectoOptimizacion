const contenedor = document.getElementById("contenedor")

async function pedirLibro(id) {
    const ans = await fetch(`http://127.0.0.1:5000/libro/${id}`)
    const libro = await ans.json()
    console.log(libro)
    renderizarLibro(libro)
}

function renderizarLibro(libro) {
    // Almacenamos el HTML en una variable para estructurarlo mejor
    let infoLibro = `
      <h2 id="titulo">${libro.Titulo} </h2>
      <h3 id="autor">${libro.Autor} </h3>
      <h3 id="fecha">${libro.Fecha} </h3>
      <h3 id="isbn">${libro.ISBN} </h3>
      <h3 id="editorial">${libro.Editorial} </h3>
      <h3 id="genero">${libro.Genero} </h3>
      <h3 id="paginas">${libro.Numero_pag} </h3>
      <p id ="sinopsis">${libro.Sinopsis} </p>`

    if (libro.Serie !== "No") {
        infoLibro += `<h3 id="serie">${libro.Serie} </h3>`
    }
    if (libro.Favorito) {
        infoLibro += `
        <button id="btn-favorito" onclick="modificarFavorito(${libro.id})">
            X Eliminar de Favoritos
        </button>`
    } else {
        infoLibro += `
        <button id="btn-favorito" onclick="modificarFavorito(${libro.id})">
            ❤️ Añadir a Favoritos
        </button>`
    }
    contenedor.innerHTML = infoLibro
}

async function modificarFavorito(id) {
    try {
        const respuesta = await fetch(`http://127.0.0.1:5000/modifFav/${id}`, {
            method: 'PUT'
        })
        const resultado = await respuesta.json()

        if (respuesta.ok) {
            pedirLibro(1)
        } else {
            alert(resultado.error || "No se pudo añadir a favoritos.")
        }
    } catch (error) {
        console.error("Error en la petición:", error)
        alert("Ocurrió un error al conectar con el servidor.")
    }
}

pedirLibro(1)