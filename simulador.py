from tabulate import tabulate 
# -*- coding: utf-8 -*-
#-----------------------------------
class Proceso:
    def __init__(self, nombre, prioridad, tLlegada):
        self.nombre = nombre
        self.prioridad = prioridad
        self.tLlegada = tLlegada
        self.tTermina = -1
        self.tCPU = 0
        self.tEspera = 0
        self.tIO = 0
    
    def imprime(self):
        print('Nombre: ' + self.nombre)
        print('Prioridad: ' + str(self.prioridad))
        print('Tiempo de Llegada: ' + str(self.tLlegada))
        print('Tiempo de Terminacion: ' + str(self.tTermina))
        print('Tiempo de CPU: ' + str(self.tCPU))
        print('Tiempo de Espera: ' + str(self.tEspera))
        print('Tiempo de I/O: ' + str(self.tIO))
        turnaround = self.tCPU + self.tEspera
        print('Turnaround: ' + str(turnaround))
        print('-----------------')
        
    def toArray(self):
        turnaround = self.tCPU + self.tEspera
        return [self.nombre, str(self.tLlegada), str(self.tTermina), str(self.tCPU), str(self.tEspera), str(turnaround), str(self.tIO)]

class Estado:
    def __init__(self, evento, colaDeListos, CPU, procesosBloqueados, procesosTerminados):
        self.evento = evento
        self.colaDeListos = colaDeListos
        self.CPU = CPU
        self.procesosBloqueados = procesosBloqueados
        self.procesosTerminados = procesosTerminados
    
    def imprime(self):
        print('Evento: ' + self.evento)
        print('Cola de Listos: ' + self.colaDeListos)
        print('CPU: ' + self.CPU)
        print('Procesos Bloqueados: ' + self.procesosBloqueados)
        print('Procesos Terminados: ' + self.procesosTerminados)
        print('-----------------')
        
    def toArray(self):
        return [self.evento, self.colaDeListos, self.CPU, self.procesosBloqueados, self.procesosTerminados]
#-------------------------------------
        
inputFile = open('./entrada.txt', 'r')
lineas = inputFile.readlines()
inputFile.close()

politica = lineas.pop(0).split()[0]
quantum = int(lineas.pop(0).split()[1])

listos = []
bloqueados = []
terminados = []
estados = []
enCPU = None
currentQuantum = 0

#-------------------------------------
def insertaListos(proceso, isPreemptive):
    global enCPU
    if isPreemptive:
        if enCPU.prioridad > proceso.prioridad:
            temp = enCPU
            enCPU = proceso
            insertaListos(temp, False)
            return
    listos.append(proceso)
    
    index = len(listos)-1
    while index > 0 and listos[index].prioridad < listos[index-1].prioridad:
        temp = listos[index]
        listos[index] = listos[index-1]
        listos[index-1] = temp
        index -= 1
    

#------------------------------------- 
def sumaListos(tiempo):
    for p in listos:
        p.tEspera += tiempo
        
#------------------------------------- 
def sumaBloqueados(tiempo):
    for p in bloqueados:
        p.tIO += tiempo
        
#------------------------------------- 
def sumaEnCPU(tiempo):
    if enCPU is not None:
        enCPU.tCPU += tiempo
        
#------------------------------------- 
def buscaListos(nombre):
    for i in range(len(listos)):
        if listos[i].nombre == nombre:
            return i
    return -1

#-------------------------------------
def buscaBloqueados(nombre):
    for i in range(len(bloqueados)):
        if bloqueados[i].nombre == nombre:
            return i
    return -1

#-------------------------------------
def guardarEstado(evento):
    colaDeListos = getEstadoListos()
    CPU = "-"
    if enCPU is not None:
        CPU = enCPU.nombre
    procesosBloqueados = getEstadoBloqueados()
    procesosTerminados = getEstadoTerminados()
    estados.append(Estado(evento, colaDeListos, CPU, procesosBloqueados, procesosTerminados).toArray())

#-------------------------------------
def getEstadoListos():
    if len(listos) == 0:
        return "-"
    resultado = ""
    for i in range(len(listos)):
        resultado = resultado + listos[i].nombre + " "
    return resultado

#-------------------------------------
def getEstadoBloqueados():
    if len(bloqueados) == 0:
        return "-"
    resultado = ""
    for i in range(len(bloqueados)):
        resultado = resultado + bloqueados[i].nombre + " "
    return resultado

#-------------------------------------
def getEstadoTerminados():
    if len(terminados) == 0:
        return "-"
    resultado = ""
    for i in range(len(terminados)):
        resultado = resultado + terminados[i].nombre + " "
    return resultado
#-------------------------------------
def ordenarTerminados():
    arrTerminados = []
    while len(terminados) > 0:
        minimo = -1
        indiceMinimo = -1
        for i in range(len(terminados)):
            if indiceMinimo == -1 or terminados[i].tLlegada < minimo:
                indiceMinimo = i
                minimo = terminados[i].tLlegada
        arrTerminados.append(terminados.pop(indiceMinimo).toArray())
    return arrTerminados

#-------------------------------------
def calculaEsperaPromedio():
    cantidad = len(terminados)
    suma = 0.0
    for i in range(cantidad):
        suma += terminados[i].tEspera
    return suma/cantidad

#-------------------------------------
def calculaTurnaroundPromedio():
    cantidad = len(terminados)
    suma = 0.0
    for i in range(cantidad):
        suma += terminados[i].tEspera + terminados[i].tCPU
    return suma/cantidad

#------------------------------------- 
#def prioPreemptive(isPreemptive):
#    global enCPU
#    for i in range(len(lineas)):
#        words = lineas[i].split()
#        
#        if words[1] == 'Llega':
#            nuevo = Proceso(words[2], words[4], int(words[0]))
#            if len(listos) == 0 and enCPU is None:
#                enCPU = nuevo
#            else:
#                insertaListos(nuevo, isPreemptive)
#            print('Proceso ' + words[2] + ' creado' + ' en tiempo: ' + words[0])
#            
#        elif words[1] == 'Acaba':
#            if enCPU.nombre == words[2]:
#                enCPU.tTermina = int(words[0])
#                terminados.append(enCPU)
#                enCPU = None
#                if len(listos) > 0:
#                    enCPU = listos.pop(0)
#            else:
#                indiceListos = buscaListos(words[2])
#                if indiceListos != -1:
#                    listos[indiceListos].tTermina = int(words[0])
#                    terminados.append(listos.pop(indiceListos))
#                else:
#                    indiceBloqueados = buscaBloqueados(words[2])
#                    if indiceBloqueados != -1:
#                        bloqueados[indiceBloqueados].tTermina = int(words[0])
#                        terminados.append(bloqueados.pop(indiceBloqueados))
#            print('Proceso ' + words[2] + ' terminado' + ' en tiempo: ' + words[0])
#            
#        elif words[1] == 'startI/O':
#            if words[2] != enCPU.nombre:
#                print('El proceso' + words[2] + 'no puede iniciar I/O fuera del CPU')
#            elif buscaBloqueados(words[2]) != -1:
#                print('El proceso' + words[2] + 'no puede iniciar otra operacion de I/O')
#            else:
#                bloqueados.append(enCPU)
#                enCPU = None
#                if len(listos) > 0:
#                    enCPU = listos.pop(0)
#            print('Proceso ' + words[2] + ' startI/O' + ' en tiempo: ' + words[0])
#            
#        elif words[1] == 'endI/O':
#            indiceBloqueados = buscaBloqueados(words[2])
#            if indiceBloqueados == -1:
#                print('El proceso no estaba bloqueado')
#            else:
#                insertaListos(bloqueados.pop(indiceBloqueados), isPreemptive)
#            print('Proceso ' + words[2] + ' endI/O' + ' en tiempo: ' + words[0])
#        
#        guardarEstado(lineas[i])
#        if lineas[i+1].split()[0] != 'FinSimulacion':
#            tiempo = int(lineas[i+1].split()[0]) - int(words[0])
#            sumaListos(tiempo)
#            sumaBloqueados(tiempo)
#            sumaEnCPU(tiempo)
#        else:
#            print(lineas[i+1].split()[0] + "\n")
#            guardarEstado(lineas[i+1].split()[0])
#            break
            
                          
        
    
#-------------------------------------
def prioScheduling(isPreemptive):
    global enCPU
    for i in range(len(lineas)):
        words = lineas[i].split()
        
        if words[1] == 'Llega':
            nuevo = Proceso(words[2], words[4], int(words[0]))
            if len(listos) == 0 and enCPU is None:
                enCPU = nuevo
            else:
                insertaListos(nuevo, isPreemptive)
            print('Proceso ' + words[2] + ' creado' + ' en tiempo: ' + words[0])
            
        elif words[1] == 'Acaba':
            if enCPU.nombre == words[2]:
                enCPU.tTermina = int(words[0])
                terminados.append(enCPU)
                enCPU = None
                if len(listos) > 0:
                    enCPU = listos.pop(0)
            else:
                indiceListos = buscaListos(words[2])
                if indiceListos != -1:
                    listos[indiceListos].tTermina = int(words[0])
                    terminados.append(listos.pop(indiceListos))
                else:
                    indiceBloqueados = buscaBloqueados(words[2])
                    if indiceBloqueados != -1:
                        bloqueados[indiceBloqueados].tTermina = int(words[0])
                        terminados.append(bloqueados.pop(indiceBloqueados))
            print('Proceso ' + words[2] + ' terminado' + ' en tiempo: ' + words[0])
            
        elif words[1] == 'startI/O':
            if words[2] != enCPU.nombre:
                print('El proceso' + words[2] + 'no puede iniciar I/O fuera del CPU')
            elif buscaBloqueados(words[2]) != -1:
                print('El proceso' + words[2] + 'no puede iniciar otra operacion de I/O')
            else:
                bloqueados.append(enCPU)
                enCPU = None
                if len(listos) > 0:
                    enCPU = listos.pop(0)
            print('Proceso ' + words[2] + ' startI/O' + ' en tiempo: ' + words[0])
            
        elif words[1] == 'endI/O':
            indiceBloqueados = buscaBloqueados(words[2])
            if indiceBloqueados == -1:
                print('El proceso no estaba bloqueado')
            else:
                insertaListos(bloqueados.pop(indiceBloqueados), isPreemptive)
            print('Proceso ' + words[2] + ' endI/O' + ' en tiempo: ' + words[0])
        
        guardarEstado(lineas[i])
        if lineas[i+1].split()[0] != 'FinSimulacion':
            tiempo = int(lineas[i+1].split()[0]) - int(words[0])
            sumaListos(tiempo)
            sumaBloqueados(tiempo)
            sumaEnCPU(tiempo)
        else:
            print(lineas[i+1].split()[0] + "\n")
            guardarEstado(lineas[i+1].split()[0])
            break
            
    
    
#-------------------------------------
if politica == "prioNotPreemptive":
    prioScheduling(False)
elif politica == "prioPreemptive":
    prioScheduling(True)
else:
    print("No.")

esperaPromedio = calculaEsperaPromedio()
turnaroundPromedio = calculaTurnaroundPromedio()
arrTerminados = ordenarTerminados()

headersEstados = ['Evento', 'Cola de listos', 'CPU', 'Procesos Bloqueados', 'Terminados']
headersProcesos = ['Proceso', 'Tiempo de Llegada', 'Tiempo de Terminacion', 'Tiempo de CPU', 'Tiempo de Espera', 'Turnaround', 'Tiempo de I/O']

    
print(tabulate(estados, headers=headersEstados))
print("\n")
print(tabulate(arrTerminados, headers=headersProcesos))
print("\n")
print('Espera Promedio: ' + str(round(esperaPromedio, 2)))
print('Turnaround Promedio: ' + str(round(turnaroundPromedio, 2)))
