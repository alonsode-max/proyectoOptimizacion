const contenedor = document.getElementById("contenedor")

const LibroTest = {
    titulo: "Dragon Ball Super 2",
    autor: "Akira Toriyama",
    fecha: "2025-02-07",
    ISBN: "4156484",
    editorial: "Editorial planeta",
    genero: "Juvenil",
    paginas: "200",
    serie: "Dragon ball",
    sinopsis: "Bla bla bla blablablabla bla blablabla blablablablablablablablabalbalbalbalablabalbabbla blablabal blabla  blablablabalbalbalbal blablabla  bal bla bla bla bla blablablabalbalbalbalbalbdshlabhcjosdalbhduyofldkqwh iewqg fyqeiubgvyfuebwiqhafuoiewhqf8ucoewbgquviogequviowfgveuioqwcbgfeiuowqgvfiuewoqgvfueiocgsauidgfeiuowhqfndkjsbgfhiuelwb gqfiovwqiuobcgehsuisqbgfuoeqw"
}

async function pedirLibro(index) {
    const ans = await fetch("")//Poner link del libro
    const libro = ans.json()
    console.log(libro)
    renderizarLibro(libro)
}


function renderizarLibro(libro) {
    contenedor.innerHTML = `
      <h2 id="titulo">${libro.titulo} </h2>
      <h3 id="autor">${libro.autor} </h3>
      <h3 id="fecha">${libro.fecha} </h3>
      <h3 id="isbn">${libro.ISBN} </h3>
      <h3 id="editorial">${libro.editorial} </h3>
      <h3 id="genero">${libro.genero} </h3>
      <h3 id="paginas">${libro.paginas} </h3>
      <h3 id="serie">${libro.serie} </h3>
      <p id ="sinopsis">${libro.sinopsis} </p>`
}

renderizarLibro(LibroTest)
