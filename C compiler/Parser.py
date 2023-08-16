# -*- coding: utf-8 -*-


from Lexer import CLexer
from sly import Parser
import sys
import os
import re
from Clases import *


class CParser(Parser):
    nombre_fichero = ''
    tokens = CLexer.tokens
    debugfile = "salida.out"

    precedence = (
        ('right', '='),
        ('left', '!'),
        ('nonassoc', 'LE', 'GE', '<', '>', 'EQUAL', 'DIFFERENT'),
        ('left', "+", 'SUB'),
        ('left', "*", "/"),
        ) 

    #####################################   PROGRAMA   #####################################
    @_('caracteristicas')
    def program(self, p):
        print()
        print(p[0])
        print()
        return Programa(secuencia= p[0])

    

    #####################################   CARACTERISTICA   #####################################   
    @_('')
    def caracteristicas(self, p):
        return []
    
    @_('caracteristicas caracteristica')
    def caracteristicas(self, p):
        return p[0] + [p[1]]
    
    @_('metodo')
    def caracteristica(self, p):
        return p[0]
    
    @_('atributo')
    def caracteristica(self, p):
        return p[0] 
    

    #####################################   ATRIBUTO   #####################################
    @_('declaracion ";"')
    def atributo(self, p):
        return Atributo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre=p[0][1],
            cuerpo=NoExpr()
        )
    
    @_('declaracion "=" expr ";"')
    def atributo(self, p):
        return Atributo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre=p[0][1],
            cuerpo=Asignacion(linea = p.lineno,
                              nombre=p[0][1],
                              cuerpo=p[2])
        )

    #####################################   METODO   #####################################
    @_('declaracion "(" parametros ")" "{" exprs "}"')
    def metodo(self, p):
        return Metodo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre= p[0][1],
            formales=p[2],
            cuerpo=p[5]
        )
    
    @_('declaracion "(" parametros ")" "{" "}"')
    def metodo(self, p):
        return Metodo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre= p[0][1],
            formales=p[2],
            cuerpo=NoExpr()
        )
    
    @_('declaracion "(" parametros ")" ";"')
    def metodo(self, p):
        return Metodo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre= p[0][1],
            formales=p[2],
            cuerpo=NoExpr()
        )

    #####################################  PARAMETRO  #####################################
    @_('parametros "," parametro')
    def parametros(self, p):
        return p[0] + [p[2]]
    
    @_('parametro')
    def parametros(self, p):
        return [p[0]]
    
    @_('')
    def parametros(self, p):
        return []
    
    @_('declaracion')
    def parametro(self, p):
        return Formal(
            linea= p.lineno,
            tipo = p[0][0],
            nombre_variable= p[0][1]
        )

    #####################################   EXPR   #####################################
    @_('exprs expr')
    def exprs(self, p):
        return p[0] + [p[1]]
    
    @_('exprs expr ";"')
    def exprs(self, p):
        return p[0] + [p[1]]
    
    @_('expr')
    def exprs(self, p):
        return [p[0]]
    
    @_('exprs_coma expr ","')
    def exprs_coma(self, p):
        return p[0] + [p[1]]
    
    @_('expr ","')
    def exprs_coma(self, p):
        return [p[0]]
    
    @_('declaracion ";"')
    def expr(self, p):
        return Atributo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre=p[0][1],
            cuerpo=NoExpr()
        )

    
    @_('IDENTIFIER "=" expr ";"')
    def expr(self, p):
        return Asignacion(
            p.lineno,
            nombre=p[0],
            cuerpo=p[2])
    
    @_('declaracion "=" expr ";"')
    def expr(self, p):
        return Atributo(
            linea=p.lineno,
            tipo=p[0][0],
            nombre=p[0][1],
            cuerpo=Asignacion(linea = p.lineno,
                              nombre=p[0][1],
                              cuerpo=p[2])
        )
    
    
    @_('IDENTIFIER PLUSEQ expr')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Suma(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=p[2],
                        )
        )
    @_('IDENTIFIER PLUSEQ expr ";"')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Suma(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=p[2],
                        )
        )
    
    @_('IDENTIFIER MINUSEQ expr')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Resta(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=p[2],
                        )
        )
    @_('IDENTIFIER MINUSEQ expr ";"')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Resta(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=p[2],
                        )
        )
    
    @_('IDENTIFIER PLUSPLUS')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Suma(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=Entero(p.lineno, 1),
                        )
        )
    @_('IDENTIFIER PLUSPLUS ";"')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Suma(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=Entero(p.lineno, 1),
                        )
        )
    
    @_('IDENTIFIER MINUSMINUS')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Resta(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=Entero(p.lineno, 1),
                        )
        )
    @_('IDENTIFIER MINUSMINUS ";"')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre=p[0],
            cuerpo=Resta(linea=p.lineno,
                        izquierda=Objeto(p.lineno, p[0]),
                        derecha=Entero(p.lineno, 1),
                        )
        )
    
    
    @_('IDENTIFIER "(" exprs_coma expr ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, nombre_metodo=p[0], argumentos=p[2] + [p[3]])
    
    
    @_('IDENTIFIER "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, nombre_metodo=p[0], argumentos = [p[2]])
    
    @_('IDENTIFIER "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, nombre_metodo=p[0])
    
    
    @_('IF "(" expr ")" "{" exprs "}" elseifs')
    def expr(self, p):
        return Condicional(
            linea=p.lineno,
            condicion=p[2],
            verdadero=p[5],
            falso=p[7]
        )
    
    @_('elseifs elseif')
    def elseifs(self, p):
        return p[0] + [p[1]]
    
    @_('elseif')
    def elseifs(self, p):
        return [p[0]]
           
    @_('els')
    def elseifs(self, p):
        return p[0]
    
    @_('')
    def elseifs(self, p):
        return []
    
    @_('ELSE IF "(" expr ")" "{" exprs "}" elseifs')
    def elseif(self, p):
        return Condicional(
            linea=p.lineno,
            condicion=p[3],
            verdadero=p[6],
            falso=p[8]
        )

    @_('ELSE "{" exprs "}"')
    def els(self, p):
        return p[2]
    
    @_('')
    def els(self, p):
        return []

    @_('WHILE "(" expr ")" "{" exprs "}"')
    def expr(self, p):
        return BucleWhile(
            linea=p.lineno,
            condicion=p[2],
            cuerpo=p[5]
        )
    
    @_('FOR "(" expr expr ";" expr ")" "{" exprs "}"')
    def expr(self, p):
        return BucleFor(
            linea=p.lineno, 
            iter=p[2],
            condicion=p[3],
            accion=p[5],
            cuerpo=p[8]
            )

    @_('SWITCH "(" expr ")" "{" tiposCase "}"')
    def expr(self, p):
        return Swicht(
            linea=p.lineno,
            expr=p[2],
            casos=p[5]
        )  
    
    @_('tiposCase tipoCase')
    def tiposCase(self, p):
        return p[0] + [p[1]]
    
    @_('tipoCase')
    def tiposCase(self, p):
        return [p[0]]
    
    @_('CASE expr ":" exprs')
    def tipoCase(self,p):
        return RamaCase(
            linea=p.lineno,
            valor=p[1],
            cuerpo=p[3]
        )
    
    @_('expr "+" expr')
    def expr(self, p):
        return Suma(p.lineno, p[0], p[2])

    @_('expr SUB expr')
    def expr(self, p):
        return Resta(linea=p.lineno, izquierda=p[0], derecha=p[2])

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(p.lineno, p[0], p[2])
         
    @_('expr "/" expr')
    def expr(self, p):
        return Division(p.lineno, p[0], p[2])   
    
    @_('expr "%" expr')
    def expr(self, p):
        return Modulo(p.lineno, p[0], p[2])  

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(p.lineno, p[0], p[2])
    
    @_('expr ">" expr')
    def expr(self, p):
        return Mayor(p.lineno, p[0], p[2])

    @_('expr LE expr')
    def expr(self, p):
        return MenorIgual(p.lineno, p[0], p[2])
    
    @_('expr GE expr')
    def expr(self, p):
        return MayorIgual(p.lineno, p[0], p[2])
    
    @_('expr EQUAL expr')
    def expr(self, p):
        return Igual(p.lineno, p[0], p[2])
    
    @_('expr DIFFERENT expr')
    def expr(self, p):
        return Distinto(p.lineno, p[0], p[2])

    @_('"!" expr')
    def expr(self, p):
        return Not(p.lineno, p[1])
    
    @_('"(" expr ")"')
    def expr(self, p):
        return p[1]
    
    @_('RETURN expr ";"')
    def expr(self, p):
        return Retorno(
            linea=p.lineno,
            cuerpo=p[1]
        )
    
    @_('BREAK ";"')
    def expr(self, p):
        return Break(linea=p.lineno)
    
    @_('CONTINUE ";"')
    def expr(self, p):
        return Continue(linea=p.lineno)

    @_('IDENTIFIER')
    def expr(self, p):
        return Objeto(p.lineno, p[0])
    
    @_('INT_CONST')
    def expr(self, p):
        return Entero(p.lineno, p[0])
    
    @_('CHAR_CONST')
    def expr(self, p):
        return Char(p.lineno, p[0])
    
    @_('DECIMAL_CONST')
    def expr(self, p):
        return Decimal(p.lineno, p[0])
    
    @_('STR_CONST')
    def expr(self, p):
        return String(p.lineno, p[0])
    


    #####################################   TIPO   #####################################
    @_('INT', 'CHAR', 'VOID')
    def type(self, p):
        return p[0]
    
    @_('FLOAT', 'DOUBLE', 'LONG')
    def type(self, p):
        return "float"


    #####################################   DECLARACION   #####################################
    @_('type IDENTIFIER')
    def declaracion(self, p):
        return p[0], p[1]
    


