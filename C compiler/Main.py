# -*- coding: utf-8 -*-
"""
COMPILADOR DE C

@author: Carlos Velázquez Fernández

@version: 1.0
"""

import os
import re
import sys
import traceback
from colorama import init
from termcolor import colored
init()

# CHANGE PATH TO YOUR FOLDER
DIRECTORIO = os.path.expanduser(r"C:\Users\carlos\Compiler")
sys.path.append(DIRECTORIO)

from Lexer import *
from Parser import *
from Clases import *

PRACTICA = "04" # Practica que hay que evaluar
DEBUG = True   # Decir si se lanzan mensajes de debug
NUMLINEAS = 5   # Numero de lineas que se muestran antes y después de la no coincidencia
sys.path.append(DIRECTORIO)
DIR = os.path.join(DIRECTORIO, PRACTICA)
FICHEROS = os.listdir(DIR)
TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(DIR, fich)) and
         re.search(r"^[a-zA-Z].*\.(c|test)$",fich)]
TESTS.sort()

TESTS = TESTS

passed = []
if True:
    for fich in TESTS:
        lexer = CLexer()
        f = open(os.path.join(DIR, fich), 'r', newline='')
        g = open(os.path.join(DIR, fich + '.out'), 'r', newline='')
        if os.path.isfile(os.path.join(DIR, fich)+'.nuestro'):
            os.remove(os.path.join(DIR, fich)+'.nuestro')
        if os.path.isfile(os.path.join(DIR, fich)+'.bien'):
            os.remove(os.path.join(DIR, fich)+'.bien')            
        texto = ''
        entrada = f.read()
        f.close()
        if PRACTICA == '01':
            texto = '\n'.join(lexer.salida(entrada))
            texto = f'#name "{fich}"\n' + texto
            resultado = g.read()
            g.close()
            if texto.strip().split() != resultado.strip().split():
                print(f"Revisa el fichero {fich}")
                if DEBUG:
                    texto = re.sub(r'#\d+\b','',texto)
                    resultado = re.sub(r'#\d+\b','',resultado)
                    nuestro = [linea for linea in texto.split('\n') if linea]
                    bien = [linea for linea in resultado.split('\n') if linea]
                    linea = 0
                    while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS]:
                        linea += 1
                    print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                    print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                    f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                    g = open(os.path.join(DIR, fich)+'.bien', 'w')
                    f.write(texto.strip())
                    g.write(resultado.strip())
                    f.close()
                    g.close()
                    
            else:
                passed.append(fich)

        elif PRACTICA in ('02', '03', '04'):
            parser = CParser()
            parser.nombre_fichero = fich
            parser.errores = []
            bien = ''.join([c for c in g.readlines() if c and '#' not in c])
            g.close()
            tokens = lexer.tokenize(entrada)
            j = parser.parse(tokens)
            try:
                if j and not parser.errores:
                    if PRACTICA == '02':
                        resultado = '\n'.join([c for c in j.str(0).split('\n')
                                            if c and '#' not in c])
                    
                    if PRACTICA == '03':
                        try:
                            j.Tipo()
                            resultado = '\n'.join([c for c in j.str(0).split('\n')
                                                        if c and '#' not in c])
                        except Exception as e:
                            resultado = str(fich) + ':'
                            resultado += str(e)
                            resultado += '\n' + "Compilation halted due to static semantic errors."

                    if PRACTICA == '04':
                        codigo = "from Funciones import * \n"
                        codigo += j.code(0)
                        codigo += "\nmain()\n"
                        sys.stdout = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                        
                        exec(codigo)
                        sys.stdout.close()
                        
                        sys.stdout = sys.__stdout__
                        resultado = open(os.path.join(DIR, fich)+'.nuestro', 'r').read()
                        outFich = open(os.path.join(DIR, fich)+'.out', 'r').read()
                        if resultado != outFich:
                            raise Exception (print(traceback.format_exc()))
                        
                else:
                    resultado = '\n'.join(parser.errores)
                    resultado += '\n' + "Compilation halted due to lex and parse errors"

                if resultado.lower().strip().split() != bien.lower().strip().split():
                    print(f"Revisa el fichero {fich}")
                    if DEBUG:
                        nuestro = [linea for linea in resultado.split('\n') if linea]
                        bien = [linea for linea in bien.split('\n') if linea]
                        linea = 0
                        while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS]:
                            linea += 1
                        print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                        print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                        f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                        g = open(os.path.join(DIR, fich)+'.bien', 'w')
                        f.write(resultado.strip())
                        g.write(str(bien).strip())
                        f.close()
                        g.close()
                else:
                    passed.append(fich)

            except Exception as e:
                print(traceback.format_exc())
                print(f"Lanza excepción en {fich} con el texto {e}")
                


    print("\nBIEN: ", passed, "\n")
    print("MAL: ", [x for x in TESTS if x not in passed], "\n")
    print("RESULTADO: ", len(passed), " / ", len(TESTS), "\n")

