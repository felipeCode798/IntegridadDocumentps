from flask import Flask
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
import os
import time 
import PyPDF2

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='olimpica'
app.config['MYSQL_DATABASE_DB']='integrity'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route("/")
def index():

    sql = "SELECT * FROM documents"
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()

    documents = cursor.fetchall()


    return render_template('document/index.html', documents=documents)

@app.route('/destroy/<int:id>')
def destory(id):

    conn = mysql.connect()
    cursor=conn.cursor()

    cursor.execute("DELETE FROM documents WHERE id=%s", (id))
    conn.commit()

    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id=%s", (id))
    conn.commit()
    documents = cursor.fetchall()

    return render_template('document/show.html', documents=documents)

@app.route('/update', methods=['POST'])
def update():

    _id_user = request.form['txtUser']
    _creatorName = request.form['txtCreator']
    _autorName = request.form['txtAutor']
    _producerName = request.form['txtProducer']
    _title = request.form['txtTitle']
    id = request.form['txtID']

    sql = "UPDATE documents SET id_user=%s, creator=%s, autor=%s, producer=%s, title=%s WHERE id=%s ;"
    
    data = (_id_user,_creatorName,_autorName,_producerName,_title,id)

    conn = mysql.connect()
    cursor=conn.cursor()

    cursor.execute(sql,data)

    conn.commit()

    return redirect('/')

@app.route('/create')
def create():
    return render_template('document/create.html')

@app.route('/store', methods=['POST'])
def storage():

    _name_client = request.form['txtName']
    _type_dni = request.form['txtType']
    _dni = request.form['txtDni']
    _email = request.form['txtEmail']
    _phone = request.form['txtPhone']
    _address = request.form['txtAddress']
    _product = request.form['txtProduct']
    _service = request.form['txtService']
    _city = request.form['txtCity']
    _investigator = request.form['txtInvestigator']
    _valor = request.form['txtValor']
    _document = request.files['txtDocument']

    now = datetime.now()
    time = now.strftime("%Y%H%M%S")

    if _document.filename != '':
        newName = time+_document.filename
        _document.save("uploads/"+newName)

    info_user(_name_client,_dni,_city,_email,_phone,_address)

    info_documents(_product,_service,_city,_investigator,_valor,newName)

    pdfReader = PyPDF2.PdfFileReader(_document)
    info = pdfReader.getDocumentInfo()
    ruta = 'uploads/' + newName
    creatorName = str(info.get('/Creator'))
    autorName = str(info.get('/Author'))
    creationdate = info.get('/CreationDate')
    moddate = info.get('/ModDate')
    producerName = str(info.get('/Producer'))
    title = str(info.get('/Title'))
    ultima_fecha(ruta)
    fecha = ultima_fecha(ruta)
    ultima_fecha_hora(ruta)
    hora = ultima_fecha_hora(ruta)


    # Fecha de creacion del documento
    def creacion_fecha(creationdate):

        if moddate != None:
            year = creationdate[2:6]
            day = creationdate[6:8]
            month = creationdate[8:10]
            creation_fecha = int(('{}{}{}'.format(year,day,month)))
        else:
            year = '00'
            day = '00'
            month = '00'
            creation_fecha = int(('{}{}{}'.format(year,day,month))) 

        return creation_fecha

    # Hora de creacion del documento
    def creacion_fecha_hora(creationdate):

        if moddate != None:
            hour = creationdate[10:12]
            minu = creationdate[12:14]
            secon = '00'
            cero = 0

            creation_hora = int(('{}{}{}'.format(hour,minu,secon)))
        else:
            hour = '00'
            minu = '00'
            secon = '00'
            cero = 0
            creation_hora = int(('{}{}{}'.format(hour,minu,secon)))

        return creation_hora

    # Fecha de modificacion desde metadatos
    def modifica_fecha(moddate):

        if moddate != None:
            year = moddate[2:6]
            day = moddate[6:8]
            month = moddate[8:10]
            modifi = int(('{}{}{}'.format(year,day,month)))
        else:
            year = '00'
            day = '00'
            month = '00'
            modifi = int(('{}{}{}'.format(year,day,month)))

        return modifi
    
    # Hora de modificacion desde metadatos
    def modifica_fecha_hora(moddate):

        if moddate != None:
            hour = moddate[10:12]
            minu = moddate[12:14]
            secon = '00'
            cero = 0

            modifi_hora = int(('{}{}{}'.format(hour,minu,secon)))
        else:
            creationdate = info.get('/CreationDate')
            hour = creationdate[10:12]
            minu = creationdate[12:14]
            secon = '00'
            cero = 0

            modifi_hora = int(('{}{}{}'.format(hour,minu,secon)))

        return modifi_hora
    
    creacion_fecha = creacion_fecha(creationdate)
    creacion_fecha_hora = creacion_fecha_hora(creationdate)

    modifica_fecha = modifica_fecha(moddate)
    modifica_fecha_hora = modifica_fecha_hora(moddate)  

    id = consulta_id()

    sql = "UPDATE documents SET creator = %s,autor = %s,producer = %s,title = %s,creation_date = %s,modification_date = %s,last_date = %s WHERE id ="+str(id)
    data = (creatorName,autorName,producerName,title,creacion_fecha,modifica_fecha,fecha)
    
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

    creatorCont = contar_creator(creatorName)
    authorCont = contar_author(autorName)
    producerCont = contar_producer(producerName)
    analisis(creacion_fecha, creacion_fecha_hora, modifica_fecha, modifica_fecha_hora, fecha, hora, creatorCont, authorCont, producerCont, creatorName, autorName, producerName, _name_client, _phone, _dni)
    resultado = analisis(creacion_fecha, creacion_fecha_hora, modifica_fecha, modifica_fecha_hora, fecha, hora, creatorCont, authorCont, producerCont, creatorName, autorName, producerName, _name_client, _phone, _dni)

    #data = (creatorName, autorName, producerName, title, creacion_fecha, creacion_fecha_hora, modifica_fecha, modifica_fecha_hora, fecha, hora, resultado)
    data = (resultado)
    data = list(data)

    return render_template('document/prueba.html', data=data)

def ultima_fecha(ruta):

    estado = os.stat(ruta)
    ultima_fe = time.localtime(estado.st_mtime)
    day = int(ultima_fe[0]) 
    month = int(ultima_fe[1])
    year = int(ultima_fe[2])
    cero = 0

    if month < 10:
        month = ('{}{}'.format(cero,month))

    if year < 10:
        year = ('{}{}'.format(cero,year))

    ultima_fe = int(('{}{}{}'.format(day,month,year)))

    return ultima_fe

# Funcion para ver la hora de modificacion vista desde el pc
def ultima_fecha_hora(ruta):

    estado = os.stat(ruta)
    ultima_fe = time.localtime(estado.st_mtime)    
    hora = int(ultima_fe[3])
    minu = int(ultima_fe[4])
    secon = '00'
    cero = 0

    if hora < 10:
        hora = ('{}{}'.format(cero,hora))

    if minu < 10:
        minu = ('{}{}'.format(cero,minu))
    
    hour = int(('{}{}{}'.format(hora,minu,secon)))
    
    return hour 

#insertar Usuario
def info_user(_name_client,_dni,_city,_email,_phone,_address):

    sql = "INSERT INTO users(name,dni,id_ciudad,phone,email,address) VALUES(%s,%s,%s,%s,%s,%s) "
    data = (_name_client,_dni,_city,_email,_phone,_address)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def info_documents(_product,_service,_city,_investigator,_valor,newName):

    sql = "INSERT INTO documents(product,service,id_city,id_investigator,value,document) VALUES(%s,%s,%s,%s,%s,%s)"
    data = (_product,_service,_city,_investigator,_valor,newName)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def data_documents(creatorName,autorName,producerName,title,creacion_fecha,modifica_fecha,fecha):

    sql = "INSERT INTO documents(creator,autor,producer,title,creation_date,modification_date,last_date) VALUES(%s,%s,%s,%s,%s,%s)"
    data = (creatorName,autorName,producerName,title,creacion_fecha,modifica_fecha,fecha)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def consulta_id():

    sql = "SELECT id FROM documents ORDER BY id DESC LIMIT 1"
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()

    data = cursor.fetchone()

    dataId = data[0]

    return dataId

def apocrifo():

    consulta_id()
    id = str(consulta_id())
    status = 'APOCRIFO'

    sql = "UPDATE documents SET status = %s WHERE id = '" + id + "'" 
    data = (status)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni):

    sql = "INSERT INTO apocrypha(creator,autor,producer,name,phone,dni) VALUES(%s,%s,%s,%s,%s,%s)"
    data = (creatorName,autorName,producerName,_name_client,_phone,_dni)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def autentico():

    consulta_id()
    id = str(consulta_id())

    status = 'AUTENTICO'

    sql = "UPDATE documents SET status = %s WHERE id = " + id  
    data = (status)

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,data)
    conn.commit()

def contar_creator(creatorName):

    creatorName = str(creatorName)
    sql = "SELECT COUNT(*) FROM listblack WHERE creator = '" + creatorName + "'" 
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()

    data = cursor.fetchone()

    contCreator = data[0]

    return contCreator

def contar_author(autorName):

    sql = "SELECT COUNT(*) FROM apocrypha WHERE autor = '" + autorName + "'" 
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()

    data = cursor.fetchone()

    contAuthor = data[0]

    return contAuthor

def contar_producer(producerName):

    sql = "SELECT COUNT(*) FROM listblack WHERE producer = '" + producerName + "'" 
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()

    data = cursor.fetchone()

    contProducer = data[0]

    return contProducer

def analisis(creacion_fecha, creacion_fecha_hora, modifica_fecha, modifica_fecha_hora, fecha, hora, creatorCont, authorCont, producerCont, creatorName, autorName, producerName, _name_client, _phone, _dni):

    date = creacion_fecha + 9305
    #hour = creacion_fecha_hora + 53500
    hour = 144500

    if creatorCont >= 1:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 1")
    elif authorCont >= 1:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo o el autor de este docuemneto ha intentado subir documentos posiblemente apocrifos anteriormente"
        print("Por caso 2")
    elif producerCont >= 1:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 3")
    elif creacion_fecha != modifica_fecha:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 4")
    elif creacion_fecha_hora != modifica_fecha_hora:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 5")
    elif creacion_fecha == 00000000:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 6")
    elif date > fecha:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 7")
    elif hour > hora:
        apocrifo()
        inserapocrifo(creatorName,autorName,producerName,_name_client,_phone,_dni)
        resultado = "Este docuemto posiblemente es apocrifo"
        print("Por caso 8")
        print(hora)
        print(hour)
    else:
        autentico()
        resultado = "Este docuemto es autentico"
        print("Por caso 9")

    return resultado

if __name__ == '__main__':
    app.run(debug=True)