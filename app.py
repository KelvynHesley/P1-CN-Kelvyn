from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'server-bd-cn1.mysql.database.azure.com',
    'user': 'useradmin',
    'password': 'admin@123',
    'database': 'locadora_db_kelvyn'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/veiculos')
def listar_veiculos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM veiculos ORDER BY marca, modelo")
    veiculos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('veiculos.html', veiculos=veiculos)

@app.route('/veiculos/form', methods=['GET', 'POST'])
@app.route('/veiculos/form/<int:id>', methods=['GET', 'POST'])
def formulario_veiculo(id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    veiculo = {}
    if id:
        cursor.execute("SELECT * FROM veiculos WHERE id = %s", (id,))
        veiculo = cursor.fetchone()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        placa = request.form['placa']
        disponibilidade = 'disponibilidade' in request.form

        if id:
            sql = "UPDATE veiculos SET marca=%s, modelo=%s, ano=%s, placa=%s, disponibilidade=%s WHERE id=%s"
            cursor.execute(sql, (marca, modelo, ano, placa, disponibilidade, id))
        else:
            sql = "INSERT INTO veiculos (marca, modelo, ano, placa, disponibilidade) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (marca, modelo, ano, placa, disponibilidade))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_veiculos'))

    cursor.close()
    conn.close()
    return render_template('veiculo_form.html', veiculo=veiculo)

@app.route('/veiculos/delete/<int:id>')
def deletar_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM veiculos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('listar_veiculos'))

@app.route('/clientes')
def listar_clientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/form', methods=['GET', 'POST'])
@app.route('/clientes/form/<int:id>', methods=['GET', 'POST'])
def formulario_cliente(id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cliente = {}
    if id:
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        cliente = cursor.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']

        if id:
            sql = "UPDATE clientes SET nome=%s, email=%s, telefone=%s WHERE id=%s"
            cursor.execute(sql, (nome, email, telefone, id))
        else:
            sql = "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, email, telefone))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_clientes'))

    cursor.close()
    conn.close()
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/delete/<int:id>')
def deletar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('listar_clientes'))

@app.route('/locacoes')
def listar_locacoes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT l.id, c.nome as cliente, v.modelo as veiculo, v.placa, 
               DATE_FORMAT(l.data_inicio, '%d/%m/%Y') as data_inicio, 
               DATE_FORMAT(l.data_fim, '%d/%m/%Y') as data_fim, l.valor
        FROM locacoes l
        JOIN clientes c ON l.id_cliente = c.id
        JOIN veiculos v ON l.id_veiculo = v.id
        ORDER BY l.data_inicio DESC
    """
    cursor.execute(sql)
    locacoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('locacoes.html', locacoes=locacoes)

@app.route('/locacoes/form', methods=['GET', 'POST'])
def formulario_locacao():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        id_veiculo = request.form['id_veiculo']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        valor = request.form['valor']

        sql = "INSERT INTO locacoes (id_cliente, id_veiculo, data_inicio, data_fim, valor) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_cliente, id_veiculo, data_inicio, data_fim, valor))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_locacoes'))

    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    cursor.execute("SELECT id, modelo, placa FROM veiculos WHERE disponibilidade = TRUE ORDER BY modelo")
    veiculos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('locacao_form.html', clientes=clientes, veiculos=veiculos)

@app.route('/locacoes/delete/<int:id>')
def cancelar_locacao(id): 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM locacoes WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('listar_locacoes'))

def setup_database():
    conn = mysql.connector.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'])
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS locadora_db")
    cursor.execute("USE locadora_db")
    
    tabela_veiculos_sql = """
        CREATE TABLE IF NOT EXISTS veiculos (
            id INT AUTO_INCREMENT PRIMARY KEY, marca VARCHAR(255) NOT NULL,
            modelo VARCHAR(255) NOT NULL, ano INT, placa VARCHAR(10) UNIQUE NOT NULL,
            disponibilidade BOOLEAN DEFAULT TRUE
        )
    """
    tabela_clientes_sql = """
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL, telefone VARCHAR(20)
        )
    """
    tabela_locacoes_sql = """
        CREATE TABLE IF NOT EXISTS locacoes (
            id INT AUTO_INCREMENT PRIMARY KEY, id_cliente INT, id_veiculo INT,
            data_inicio DATE NOT NULL, data_fim DATE NOT NULL, valor DECIMAL(10, 2),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (id_veiculo) REFERENCES veiculos(id) ON DELETE CASCADE
        )
    """
    cursor.execute(tabela_veiculos_sql)
    cursor.execute(tabela_clientes_sql)
    cursor.execute(tabela_locacoes_sql)

    conn.commit()
    cursor.close()
    conn.close()
    print("Banco de dados e tabelas verificados/criados com sucesso.")

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)