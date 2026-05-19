const lista = document.getElementById("listaLibros")
const buscarNombre = document.getElementById("buscarNombre")
const filtrarGenero = document.getElementById("filtrarGenero")
const precioMax = document.getElementById("precioMax")
const ordenar = document.getElementById("ordenar")
const btnFiltrar = document.getElementById("btnFiltrar")

async function pedirLibros() {
    const params = new URLSearchParams()

    if (buscarNombre.value) params.append("nombre", buscarNombre.value)
    if (filtrarGenero.value) params.append("genero", filtrarGenero.value)
    if (precioMax.value) params.append("precio_max", precioMax.value)
    if (ordenar.value) params.append("orden", ordenar.value)

    const ans = await fetch(`http://127.0.0.1:5000/libros?${params.toString()}`)
    const data = await ans.json()

    renderizarLibros(data.libros)
    renderizarEstadisticas(data.estadisticas)
    cargarGeneros(data.libros)
}

function renderizarLibros(libros) {
    lista.innerHTML = ""

    libros.forEach(libro => {
        const card = document.createElement("div")
        card.className = "tarjeta"

        card.innerHTML = `
            <h3>${libro.Titulo}</h3>
            <p>${libro.Autor}</p>
            <p><strong>${libro.Genero}</strong></p>
            <p>${libro.Precio} €</p>
            <button class="favBtn">⭐ Favorito</button>
        `

        // BOTÓN DE FAVORITOS FUNCIONAL
        card.querySelector(".favBtn").onclick = () => marcarFavorito(libro.id)

        lista.appendChild(card)
    })
}

async function marcarFavorito(id) {
    // ESTA ES LA RUTA CORRECTA SEGÚN TU PYTHON
    await fetch(`http://127.0.0.1:5000/modifFav/${id}`, {
        method: "PUT"
    })

    // Recargar lista y estadísticas
    pedirLibros()
}

function renderizarEstadisticas(est) {
    document.getElementById("totalLibros").textContent = `Total libros: ${est.total}`
    document.getElementById("promedioPrecio").textContent = `Precio medio: ${est.promedio_precio} €`
    document.getElementById("categoriaMas").textContent = `Género más usado: ${est.categoria_mas_utilizada}`
    document.getElementById("masCaro").textContent = `Más caro: ${est.mas_caro}`
    document.getElementById("cantidadFav").textContent = `Favoritos marcados: ${est.cantidad_favoritos}`
}

function cargarGeneros(libros) {
    const generos = [...new Set(libros.map(l => l.Genero))]

    filtrarGenero.innerHTML = `<option value="">Género</option>`

    generos.forEach(g => {
        filtrarGenero.innerHTML += `<option value="${g}">${g}</option>`
    })
}

btnFiltrar.onclick = pedirLibros

pedirLibros()
