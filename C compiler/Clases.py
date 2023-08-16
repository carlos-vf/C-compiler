# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from operator import itemgetter
from typing import List
from collections.abc import Iterable
import copy


class Ambito():
    
    def __init__(self):
        self.reset()
        
    def reset(self):

        # Pila de atributos (key = nombre de variable, value = tipo)
        self.pila = []
        
        # Dic (key = nombre metodo, value = [[[a0, t0], ... ,[an, tn]], return type]
        self.metodos = {'printf':[[['','string'],['','']],'void']}  
        
    ############################# ATRIBUTOS ###############################
    def tipoAtributo(self, nombre):
        for i in range(len(self.pila)-1, 0, -1):
            if nombre in self.pila[i]:
                return self.pila[i][nombre]
    
    def checkAtributo(self, nombre):
        for i in range(len(self.pila)-1, 0, -1):
            if nombre in self.pila[i]:
                return True
        return False

         
    ############################# METODOS ###############################    
    def checkMetodo(self, nombre):
        if nombre in self.metodos:
            return True
        else:
            return False

        
    ############################# AMBITOS ############################### 
    def enterScope(self):
        if len(self.pila) == 0:
            self.pila.append(copy.copy({}))
        else:
            self.pila.append(copy.copy(self.pila[-1]))
        
    def findSymbol(self, nombre):
        return self.pila[-1][nombre]
    
    def addSymbol(self, x):
        if isinstance(x, Formal):
            self.pila[-1][x.nombre_variable] = x.tipo
        else:
            self.pila[-1][x.nombre] = x.tipo
        
    def checkScope(self, x):
        if x in self.pila[-1].keys():
            return True
        else:
            return False
        
    def exitScope(self):
        self.pila.pop()
        
    #####################################################################
    


@dataclass
class Nodo:
    linea: int = 0

    def str(self, n):
        return f'{n*" "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_type'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_formal\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        return resultado
    
    def code(self, n):
        codigo =  f'{" "*n}{self.nombre_variable}: {self.tipo}'
        return codigo


class Expresion(Nodo):
    cast: str = '_no_type'


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_assign\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.nombre} = {self.cuerpo.code(0)}'
        return codigo
    
    def Tipo(self, Ambito):
        tipoNombre = Ambito.tipoAtributo(self.nombre)
        self.cuerpo.Tipo(Ambito)
        tipoCuerpo = self.cuerpo.cast
     
        # Comprobacion de tipos
        if tipoCuerpo != tipoNombre:
            raise Exception(f'{self.linea}: Type {tipoCuerpo} of assigned expression does not \
                            conform to declared type {tipoNombre} of identifier {self.nombre}.')
        else: 
            self.cast = tipoNombre
        



@dataclass
class LlamadaMetodo(Expresion):
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dispatch\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = ""
        codigo += f'{" "*n}{self.nombre_metodo}('
        for i in range(0, len(self.argumentos)):
            if isinstance(self.argumentos[i], Objeto):
                codigo += f'{self.argumentos[i].code(0)}'
            else:
                codigo += f'{self.argumentos[i].code(0)}'
            if i != (len(self.argumentos) - 1):
                codigo += f', '    
        codigo += f')'

        return codigo
    
    def Tipo(self, Ambito):

        # Comprobar si el metodo esta definido
        c = Ambito.checkMetodo(self.nombre_metodo)
        if c != False:
            metodo = Ambito.metodos[self.nombre_metodo]
        else:
            raise Exception(f'{self.linea}: Dispatch to undefined method {self.nombre_metodo}.')
        # Comprobacion del tipo de los argumentos
        for i in range(len(self.argumentos)):
            self.argumentos[i].Tipo(Ambito)
            if self.argumentos[i].cast != metodo[0][i][1] and metodo[0][i][1] != '':
                raise Exception(f'{self.linea}: In call of method {self.nombre_metodo}, \
                                type {self.argumentos[i].cast} of parameter {metodo[0][i][0]} does not \
                                conform to declared type {metodo[0][i][1]}.')
                
        # Tipo de retorno
        self.cast = metodo[1]      


@dataclass
class Condicional(Expresion):
    condicion: Expresion = None
    verdadero: List[Expresion] = field(default_factory=list)
    falso: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_cond\n'
        resultado += self.condicion.str(n+2)
        resultado += f'{(n+2)*" "}_true\n'
        resultado += ''.join([e.str(n+4) for e in self.verdadero])
        resultado += f'{(n+2)*" "}_false\n'
        if isinstance(self.falso, Iterable):
            resultado += ''.join([e.str(n+4) for e in self.falso])
        else:
            resultado += self.falso.str(n+4)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}if {self.condicion.code(0)} :\n'
        for expr in self.verdadero:
            codigo += f'{" "*(n+2)}{expr.code(0)}\n'

        """ for e in self.falso:
            if isinstance(e, Condicional):
                codigo += f'{" "*n}elif ({e.condicion.code(0)}):\n'
                for expr in e.verdadero:
                    codigo += f'{" "*(n+2)}{expr.code(0)}\n'
                codigo += f'{" "*n}else:\n'
                if e.falso == []:
                    codigo += f'{" "*(n+2)}pass\n'
                for expr in e.falso:
                    codigo += f'{" "*(n+2)}{expr.code(0)} \n'
            else:
                codigo += f'{" "*n}else:\n'
                for expr in e:
                    codigo += f'{" "*(n+2)}{expr.code(0)} \n' """
        
        if isinstance(self.falso, Condicional):
            codigo += f'{" "*n}elif ({e.condicion.code(0)}):\n'
            for expr in e.verdadero:
                codigo += f'{" "*(n+2)}{expr.code(0)}\n'
            codigo += f'{" "*n}else:\n'
            if e.falso == []:
                codigo += f'{" "*(n+2)}pass\n'
            for expr in e.falso:
                codigo += f'{" "*(n+2)}{expr.code(0)} \n'

        else:
            codigo += f'{" "*n}else:\n'
            for expr in self.falso:
                codigo += f'{" "*(n+2)}{expr.code(0)} \n' 

        if self.falso == []:
            codigo += f'{" "*(n+2)}pass\n'

        return codigo

    def Tipo(self, Ambito):
        Ambito.enterScope()
        self.condicion.Tipo(Ambito)

        for expr in self.verdadero:
            if isinstance(expr, Atributo):
                Ambito.addSymbol(expr)
            expr.Tipo(Ambito)

        for expr in self.falso:
            if isinstance(expr, Atributo):
                Ambito.addSymbol(expr)
            expr.Tipo(Ambito)

        self.cast = "void"
        Ambito.exitScope()


@dataclass
class BucleWhile(Expresion):
    condicion: Expresion = None
    cuerpo: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_while_loop\n'
        resultado += self.condicion.str(n+2)
        resultado += ''.join([e.str(n+4) for e in self.cuerpo])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}while {self.condicion.code(0)}:\n'
        for expr in self.cuerpo:
            codigo += expr.code(n+2) + '\n'
        return codigo
    
    def Tipo(self, Ambito):
        Ambito.enterScope()

        self.condicion.Tipo(Ambito)
        if self.condicion.cast != 'bool':
            raise Exception(f'{self.linea}: Loop condition does not have type bool.')
        
        for expr in self.cuerpo:
            if isinstance(expr, Atributo):
                Ambito.addSymbol(expr)
            expr.Tipo(Ambito)

        self.cast = 'void'
        Ambito.exitScope()
    

@dataclass
class BucleFor(Expresion):
    iter: Expresion = None
    condicion: Expresion = None
    accion: Expresion = None
    cuerpo: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_for_loop\n'
        resultado += self.iter.str(n+2)
        resultado += self.condicion.str(n+2)
        resultado += self.accion.str(n+2)
        resultado += ''.join([e.str(n+4) for e in self.cuerpo])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.iter.code(0)}\n'
        codigo += f'{" "*n}while {self.condicion.code(0)}:\n'
        for expr in self.cuerpo:
            codigo += expr.code(n+2) + '\n'
        codigo += self.accion.code(n+2) + '\n'
        return codigo
    
    def Tipo(self, Ambito):

        Ambito.enterScope()
        if isinstance(self.iter, Atributo):
            Ambito.addSymbol(self.iter)

        self.iter.Tipo(Ambito)
        self.condicion.Tipo(Ambito)
        self.accion.Tipo(Ambito)
        
        if self.condicion.cast != 'bool':
            raise Exception(f'{self.linea}: Loop condition does not have type bool.')

        for expr in self.cuerpo:
            if isinstance(expr, Atributo):
                Ambito.addSymbol(expr)
            expr.Tipo(Ambito)

        self.cast = 'void'

        Ambito.exitScope()

        


@dataclass
class RamaCase(Expresion):
    valor: Expresion = None
    cuerpo: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += ''.join([c.str(n+2) for c in self.cuerpo])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}case {self.valor.code(0)}:\n'
        for expr in self.cuerpo:
            if not isinstance(expr, Break):
                codigo += expr.code(n+2) + '\n'
        return codigo

    def Tipo(self, Ambito):
        self.valor.Tipo(Ambito)

        Ambito.enterScope()
        for expr in self.cuerpo:
            if isinstance(expr, Atributo):
                Ambito.addSymbol(expr)
            expr.Tipo(Ambito)
        Ambito.exitScope()
        
        self.cast = 'void'


@dataclass
class Swicht(Expresion):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_typcase\n'
        resultado += self.expr.str(n+2)
        resultado += ''.join([c.str(n+2) for c in self.casos])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}match {self.expr.code(0)}:\n'
        for expr in self.casos:
            codigo += expr.code(n+2) + '\n'
        return codigo
    
    def Tipo(self, Ambito):
        self.expr.Tipo(Ambito)
        for caso in self.casos:
            caso.Tipo(Ambito)
        self.cast = 'void'


@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion = None
    derecha: Expresion = None

    def code(self, n):
        codigo = f'{" "*n}{self.izquierda.code(0)} {self.operando} {self.derecha.code(0)}'
        return codigo


@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_plus\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.derecha.cast == 'int' or self.derecha.cast == 'float'):
            self.cast = self.derecha.cast
        else:
            raise Exception(f'{self.linea}: non-numerical arguments: {self.izquierda.cast} + {self.derecha.cast}')


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_sub\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.derecha.cast == 'int' or self.derecha.cast == 'float'):
            self.cast = self.derecha.cast
        else:
            raise Exception(f'{self.linea}: non-numerical arguments: {self.izquierda.cast} + {self.derecha.cast}')


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mul\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.derecha.cast == 'int' or self.derecha.cast == 'float'):
            self.cast = self.derecha.cast
        else:
            raise Exception(f'{self.linea}: non-numerical arguments: {self.izquierda.cast} + {self.derecha.cast}')



@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_divide\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.derecha.cast == 'int' or self.derecha.cast == 'float'):
            self.cast = self.derecha.cast
        else:
            raise Exception(f'{self.linea}: non-numerical arguments: {self.izquierda.cast} + {self.derecha.cast}')
    

@dataclass
class Modulo(OperacionBinaria):
    operando: str = '%'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mod\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.derecha.cast == 'int'):
            self.cast = self.derecha.cast
        else:
            raise Exception(f'{self.linea}: non-numerical arguments: {self.izquierda.cast} + {self.derecha.cast}')


@dataclass
class Mayor(OperacionBinaria):
    operando: str = '>'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_gt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.izquierda.cast == 'int' or self.izquierda.cast == 'float'):
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in > statement.')
        

@dataclass
class MayorIgual(OperacionBinaria):
    operando: str = '>='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_ge\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.izquierda.cast == 'int' or self.izquierda.cast == 'float'):
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in >= statement.')
    

@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_lt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.izquierda.cast == 'int' or self.izquierda.cast == 'float'):
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in < statement.')
        

@dataclass
class MenorIgual(OperacionBinaria):
    operando: str = '<='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_le\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if (self.izquierda.cast == self.derecha.cast) and (self.izquierda.cast == 'int' or self.izquierda.cast == 'float'):
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in <= statement.')


@dataclass
class Igual(OperacionBinaria):
    operando: str = '=='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_eq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in == statement.')
    

@dataclass
class Distinto(OperacionBinaria):
    operando: str = '!='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dist\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = 'bool'
        else:
            raise Exception(f'{self.linea}: Error in != statement.')



@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = '!'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_not\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}not {self.expr.code(0)}'
        return codigo
    
    def Tipo(self, Ambito):
        self.expr.Tipo(Ambito)
        if (self.expr.cast == "bool") or (self.expr.cast == "int"):
            self.cast = "Bool"
        else:
            raise Exception(f'{self.linea}: Error in negation statement.')
        

@dataclass
class Objeto(Expresion):
    nombre: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.nombre}'
        return codigo
    
    def Tipo(self, Ambito):
        
        if Ambito.checkScope(self.nombre):
            self.cast = Ambito.findSymbol(self.nombre)
        elif Ambito.checkAtributo(self.nombre):
            self.cast = Ambito.tipoAtributo(self.nombre)
        else:
            raise Exception(f'{self.linea}: Undeclared identifier {self.nombre}.')


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_no_expr\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.cast = '_no_type'


@dataclass
class Entero(Expresion):
    valor: int = 0

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_int\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.valor}'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = "int"

    
@dataclass
class Decimal(Expresion):
    valor: float = 0.0

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_float\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.valor}'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = "float"

    
@dataclass
class Char(Expresion):
    valor: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_char\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        v = self.valor[1:-1]
        codigo = f'{" "*n}"{v}"'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = "char"


@dataclass
class String(Expresion):
    valor: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_string\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}{self.valor}'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = "string"


@dataclass
class Retorno(Expresion):
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_return\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        self.cast = self.cuerpo.cast

    def code(self, n):
        codigo = f'{" "*n}return {self.cuerpo.code(0)}'
        return codigo
    

@dataclass
class Break(Expresion):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_break\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}break'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = 'void'
    

@dataclass
class Continue(Expresion):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_continue\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def code(self, n):
        codigo = f'{" "*n}continue'
        return codigo
    
    def Tipo(self, Ambito):
        self.cast = 'void'


@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)


class Programa(IterableNodo):
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado
    
    def code(self, n):
        codigo = ""
        for caracteristica in self.secuencia:
            codigo += caracteristica.code(n)
        return codigo
    
    def Tipo(self):
        
        amb = Ambito()
        amb.enterScope()
        tmpAttr = []
        tmpMet = []
        for caracteristica in self.secuencia:
                
            # Si es metodo
            if isinstance(caracteristica, Metodo):
                args = []
                for arg in caracteristica.formales:
                    if arg.nombre_variable not in list(map(itemgetter(0), args)):
                        args.append([arg.nombre_variable, arg.tipo])
                    # Argumento redefinido
                    else:
                        raise Exception(f'{arg.linea}: Formal parameter {arg.nombre_variable} is multiply defined.')
                tmpMet.append(caracteristica.nombre)
                amb.metodos[caracteristica.nombre] = [args, caracteristica.tipo]
                
            # Si es atributo
            else:
                tmpAttr.append(caracteristica.nombre)
                amb.addSymbol(caracteristica)
        
        # Comprobar si falta el main
        if "main" not in amb.metodos:
            raise Exception('Method main is not defined.')

        # Comprobar metodos redefinidos
        dup = {x for x in tmpMet if tmpMet.count(x) > 1}
        if len(dup) > 0:
            raise Exception(f'Method {dup[0]} defined multiple times.')
        
        # Comprobar atributos globales redefinidos
        dup = {x for x in tmpAttr if tmpAttr.count(x) > 1}
        if len(dup) > 0:
            raise Exception(f'Attribute {dup[0]} defined multiple times.')
        
        for caracteristica in self.secuencia: 
            caracteristica.Tipo(amb)

        amb.exitScope()
        amb.reset()       


@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None


@dataclass
class Metodo(Caracteristica):
    formales: List[Formal] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_method\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += ''.join([c.str(n+2) for c in self.formales])
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        if isinstance(self.cuerpo, list):
            resultado += ''.join([e.str(n+2) for e in self.cuerpo])
        else:
            resultado += self.cuerpo.str(n+2)

        return resultado
    
    def code(self, n):
        codigo = f'{" "*n}def {self.nombre}('
        for i in range(0, len(self.formales)):
            codigo += self.formales[i].code(0)
            if i != (len(self.formales) - 1):
                codigo += f', '
        codigo += f'):\n'

        for expr in self.cuerpo:
            codigo += expr.code(n+2)
            codigo += ('\n')

        return codigo
    
    def Tipo(self, Ambito):

        # Anhadir argumentos al ambito 
        Ambito.enterScope()
        for formal in self.formales:
            Ambito.addSymbol(formal)
        
        # Computar tipos de las expresiones y buscar tipos de retorno
        returnTypes = []
        if not isinstance(self.cuerpo, NoExpr):
            for expr in self.cuerpo:
                if isinstance(expr, Atributo):
                    Ambito.addSymbol(expr)

                expr.Tipo(Ambito)

                if isinstance(expr, Retorno):
                    returnTypes.append(expr.cast)
        else:
            self.cuerpo.cast = "void"

        if len(returnTypes) == 0:
            returnTypes.append("void")

        
        # Comprobar que el tipo de retorno coincide con el tipo de lo que retorna el cuerpo
        for tipo in returnTypes:
            if tipo != self.tipo:
                raise Exception(f'{self.linea}: Inferred return type {tipo} of method {self.nombre} \
                                        does not conform to declared return type {self.tipo}.')

        Ambito.exitScope()


class Atributo(Caracteristica):
    
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado

    def code(self, n):
        codigo = ''
            
        if isinstance(self.cuerpo, NoExpr):
            if self.tipo == 'int':
                codigo += f'{" "*n}{self.nombre}: {self.tipo} = 0'
            elif self.tipo == 'string' or self.tipo == 'char':
                codigo += f'{" "*n}{self.nombre}: str = ""'
            elif self.tipo == 'float':
                codigo += f'{" "*n}{self.nombre}: {self.tipo} = 0.0'
            else:
                codigo += f'{" "*n}{self.nombre}: {self.tipo} = None'

        elif isinstance(self.cuerpo, Asignacion):
            codigo += f'{" "*n}{self.nombre}: {self.tipo} = {self.cuerpo.cuerpo.code(0)}'
               
        else:
            codigo += f'{" "*n}{self.nombre}: {self.tipo} = {self.cuerpo.code(0)}' 

        return codigo
    
    def Tipo(self, Ambito):
        
        self.cuerpo.Tipo(Ambito)

        if isinstance(self.cuerpo, Asignacion):
            if self.cuerpo.cast != self.tipo:
                raise Exception(f'{self.linea}: Inferred return type {self.cuerpo.cast} of {self.nombre} \
                                        does not conform to declared type {self.tipo}.')

