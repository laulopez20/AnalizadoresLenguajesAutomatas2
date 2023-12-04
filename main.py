from flask import Flask, render_template, request, jsonify
from ply import lex,yacc
from transformers import pipeline

app = Flask(__name__)

def procesarCadena(entrada):
    # Implement your logic to process the input string
    # For demonstration purposes, let's assume the processing is converting the string to uppercase
    cadenaProcesada = entrada.upper()
    return cadenaProcesada

def checkSintaxisCorrect(entrada):
    if entrada != "":
        return True
    return "Error de sintaxis"

def obtener_estrella_sentimiento(texto):
    # Cargar el analizador de sentimientos
    sentiment_analyzer = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')

    # Realizar el análisis de sentimientos
    resultado = sentiment_analyzer(texto)

    # Obtener solo la etiqueta de la polaridad (estrella)
    estrella = resultado[0]['label']

    if estrella == '5 stars' or estrella == '4 stars':
        calificacion_comentario = 'Positivo'
    elif estrella == '1 star' or estrella == '2 stars':
        calificacion_comentario = 'Negativo'
    else:
        calificacion_comentario = 'Regular'

    # Devolver la estrella
    return estrella, calificacion_comentario

# Texto que quieres analizar
texto = "No me gustan los animales pero los cuido"

# Llamar a la función y obtener la estrella del sentimiento
estrella_sentimiento = obtener_estrella_sentimiento(texto)

# Imprimir la estrella del sentimiento
print(estrella_sentimiento)

tokens = (
    'NUMERO',
    'SUMA',
    'RESTA',
    'MULTIPLICACION'
)

# Reglas de expresiones
precedence = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION'),
)

def p_expresion_binaria(t):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion'''
    if t[2] == '+':
        t[0] = t[1] + t[3]
    elif t[2] == '-':
        t[0] = t[1] - t[3]
    elif t[2] == '*':
        t[0] = t[1] * t[3]

def p_expresion_numero(t):
    'expresion : NUMERO'
    t[0] = t[1]

def p_error(t):
    print(f"Error de sintaxis en el token {t}")

t_SUMA = r'\+'
t_RESTA = r'\-'
t_MULTIPLICACION = r'\*'

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print(f'Caracter erroneo: {t.value[0]}')
    t.lexer.skip(1)

analizadorLexico = lex.lex()
analizadorSintactico = yacc.yacc()

@app.route("/analizar_lexico", methods=["POST"])
def analizar_lexico():
    entrada = request.get_json().get('inputText', '')

    # Configura el analizador léxico
    analizadorLexico.input(entrada)

    # Realiza el análisis léxico y devuelve los resultados
    resultados = []
    for token in analizadorLexico:
        resultados.append(str(token))

    return jsonify({'result': '<br>'.join(resultados)})

@app.route("/analizar_sentimiento", methods=["POST"])
def analizar_sentimiento():
    entrada = request.get_json().get('inputText', '')

    # Llamar a la función para obtener la estrella del sentimiento
    estrella, calificacion_comentario = obtener_estrella_sentimiento(entrada)

    # Devolver el resultado del análisis, la estrella y el comentario
    return jsonify({
        'result': estrella,
        'calificacion_comentario': calificacion_comentario
    })

@app.route("/", methods=["GET", "POST"])
def homepage():
    resultado_analisis = None

    if request.method == "POST":
        entrada = request.form.get("entrada")

        # Llamada a la función de análisis de sentimientos
        resultado_analisis = obtener_estrella_sentimiento(entrada)

    return render_template("index.html", title="Lenguajes y Automatas II", resultado_analisis=resultado_analisis)

@app.route("/analisis-sintactico.html")
def analisis_sintactico():
    entrada = '2 - 2 menos 2'
    resultado_sintactico = analizadorSintactico.parse(entrada)
    print(resultado_sintactico)
    return render_template("analisis-sintactico.html")


@app.route("/analisis-lexico.html", methods=["GET", "POST"])
def analisis_lexico():
    if request.method == "POST":
        entrada = request.get_json().get('inputText', '')

        # Configura el analizador léxico
        analizadorLexico.input(entrada)

        # Realiza el análisis léxico y devuelve los resultados
        resultados = []
        for token in analizadorLexico:
            resultados.append(str(token))

        return jsonify({'result': '<br>'.join(resultados)})

    return render_template("analisis-lexico.html")


if __name__ == "__main__":
    app.run(debug=True)

