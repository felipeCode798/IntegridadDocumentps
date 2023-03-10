import PyPDF2

# Abrir el archivo PDF
pdf = PyPDF2.PdfFileReader(open("C:/Users/jchav/Desktop/Prueba/ph3.pdf", "rb"))

# Obtener los metadatos del PDF
metadatos = pdf.getDocumentInfo()

# Mostrar los metadatos
for clave, valor in metadatos.items():
    print(clave, ":", valor)


