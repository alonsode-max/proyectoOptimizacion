const lista = document.getElementById("listaLibros")
const buscar = document.getElementById("buscar")
const btnBuscar = document.getElementById("btnBuscar")

async function cargarLibros() {
    const ans = await fetch("http://127.0.0.1:5000/libros")
    const data = await ans.json()

    mostrarEstadisticas(data.estadisticas)
    renderizarLibros(data.libros)
}

function mostrarEstadisticas(est) {
    document.getElementById("total").textContent = "Total libros: " + est.total
    document.getElementById("promedio").textContent = "Promedio precio: " + est.promedio_precio + "€"
    document.getElementById("masCaro").textContent = "Más caro: " + est.mas_caro
    document.getElementById("categoria").textContent = "Categoría más usada: " + est.categoria_mas_utilizada

    let top = est.top_5_mas_caros.map(l => l.Titulo + " (" + l.Precio + "€)").join(", ")
    document.getElementById("top5").textContent = "Top 5 más caros: " + top

    document.getElementById("favoritos").textContent = "Favoritos marcados: " + est.cantidad_favoritos
}

function renderizarLibros(libros) {
    lista.innerHTML = ""

    libros.forEach(libro => {
        const card = document.createElement("div")
        card.className = "tarjeta"

        card.innerHTML = `
            <h3>${libro.Titulo}</h3>
            <p>${libro.Autor}</p>
            <p>${libro.Genero}</p>
            <p>${libro.Precio} €</p>
            <button class="favBtn">⭐ Favorito</button>
        `

        card.querySelector(".favBtn").onclick = () => marcarFavorito(libro.id)

        lista.appendChild(card)
    })
}

async function marcarFavorito(id) {
    await fetch(`http://127.0.0.1:5000/añadirFav/${id}`, { method: "PUT" })
    cargarLibros()
}

btnBuscar.onclick = () => {
    filtrarPorTitulo()
}

function filtrarPorTitulo() {
    const texto = buscar.value.toLowerCase()

    const tarjetas = document.querySelectorAll(".tarjeta")

    tarjetas.forEach(t => {
        const titulo = t.querySelector("h3").textContent.toLowerCase()
        t.style.display = titulo.includes(texto) ? "block" : "none"
    })
}

cargarLibros()
