from tabulate import tabulate 
# -*- coding: utf-8 -*-
#-----------------------------------
#Clase para representar a un proceso
class Proceso:
    def __init__(self, nombre, prioridad, tLlegada):
        self.nombre = nombre #nombre del proceso
        self.prioridad = prioridad #prioridad del proceso
        self.tLlegada = tLlegada #tiempo de llegada del proceso
        self.tTermina = -1 #tiempo de terminacion del proceso, inicializado en -1 mientras no termina
        self.tCPU = 0 #tiempo de CPU del proceso
        self.tEspera = 0 #tiempo de espera del proceso
        self.tIO = 0 #tiempo de I/O del proceso
    
    def imprime(self): #funcion para imprimir los atributos de un proceso
        print('Nombre: ' + self.nombre)
        print('Prioridad: ' + str(self.prioridad))
        print('Tiempo de Llegada: ' + str(self.tLlegada))
        print('Tiempo de Terminacion: ' + str(self.tTermina))
        print('Tiempo de CPU: ' + str(self.tCPU))
        print('Tiempo de Espera: ' + str(self.tEspera))
        print('Tiempo de I/O: ' + str(self.tIO))
        turnaround = self.tCPU + self.tEspera
        print('Turnaround: ' + str(turnaround)) #el turnaround se calcula antes de imprimirse
        print('-----------------')
        
    def toArray(self): #funcion para convertir cierta instancia de un proceso en un arreglo para facilitar la creacion de la tabla
        turnaround = self.tCPU + self.tEspera
        return [self.nombre, str(self.tLlegada), str(self.tTermina), str(self.tCPU), str(self.tEspera), str(turnaround), str(self.tIO)]

class Estado: #clase para representar un estado del simulador
    def __init__(self, evento, colaDeListos, CPU, procesosBloqueados, procesosTerminados):
        self.evento = evento #evento que llego al sistema, como llegada o startI/O
        self.colaDeListos = colaDeListos #cola de procesos listos en un momento particular
        self.CPU = CPU #representa al proceso actual que esta siendo atendido por el CPU
        self.procesosBloqueados = procesosBloqueados #cola de procesos bloqueados en un momento particular
        self.procesosTerminados = procesosTerminados #cola de procesos terminados en un momento particular
    
    def imprime(self): #funcion para imprimir un estado
        print('Evento: ' + self.evento)
        print('Cola de Listos: ' + self.colaDeListos)
        print('CPU: ' + self.CPU)
        print('Procesos Bloqueados: ' + self.procesosBloqueados)
        print('Procesos Terminados: ' + self.procesosTerminados)
        print('-----------------')
        
    def toArray(self): #funcion para convertir un estado a un arreglo para facilitar la creacion de la tabla
        return [self.evento, self.colaDeListos, self.CPU, self.procesosBloqueados, self.procesosTerminados]
#-------------------------------------
        
inputFile = open('./entrada.txt', 'r') #se toma la entrada del archivo
lineas = inputFile.readlines() #se guardan todas las lineas del archivo como un arreglo de strings
inputFile.close() #se cierra el archivo

politica = lineas.pop(0).split()[0] #politica que hara el scheduler (priority preemptive o noPoreemptive)
quantum = int(lineas.pop(0).split()[1]) #quantum para las politicas en caso de ser necesario

listos = [] #arreglo para representar la cola de listos
bloqueados = [] #arreglo para representar la cola de bloqueados
terminados = [] #arreglo para representar los procesos terminados
estados = [] #arreglo para guardar los estados del simulador 
enCPU = None #proceso actual en el CPU

#-------------------------------------
#funcion para insertar un proceso a la cola de listos dependiendo del tipo de politica
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
#funcion para sumar el tiempo transcurridoa la cola de listos
def sumaListos(tiempo):
    for p in listos:
        p.tEspera += tiempo
        
#------------------------------------- 
#funcion para sumar el tiempo transcurridoa la cola de bloqueados
def sumaBloqueados(tiempo):
    for p in bloqueados:
        p.tIO += tiempo
        
#------------------------------------- 
#funcion para sumar el tiempo transcurridoa la cola de terminados
def sumaEnCPU(tiempo):
    if enCPU is not None:
        enCPU.tCPU += tiempo
        
#------------------------------------- 
#funcion para buscar un proceso en la cola de listos
def buscaListos(nombre):
    for i in range(len(listos)):
        if listos[i].nombre == nombre:
            return i
    return -1

#-------------------------------------
#funcion para buscar un proceso en la cola de bloqueados
def buscaBloqueados(nombre):
    for i in range(len(bloqueados)):
        if bloqueados[i].nombre == nombre:
            return i
    return -1

#-------------------------------------
#funcion para buscar guardar un estado en la lista
def guardarEstado(evento):
    colaDeListos = getEstadoListos()
    CPU = "-"
    if enCPU is not None:
        CPU = enCPU.nombre
    procesosBloqueados = getEstadoBloqueados()
    procesosTerminados = getEstadoTerminados()
    estados.append(Estado(evento, colaDeListos, CPU, procesosBloqueados, procesosTerminados).toArray())

#-------------------------------------
#funcion que regresa en un string los procesos en la cola de listos
def getEstadoListos():
    if len(listos) == 0:
        return "-"
    resultado = ""
    for i in range(len(listos)):
        resultado = resultado + listos[i].nombre + " "
    return resultado

#-------------------------------------
#funcion que regresa en un string los procesos en la cola de bloqueados
def getEstadoBloqueados():
    if len(bloqueados) == 0:
        return "-"
    resultado = ""
    for i in range(len(bloqueados)):
        resultado = resultado + bloqueados[i].nombre + " "
    return resultado

#-------------------------------------
#funcion que regresa en un string los procesos en la cola de  terminados
def getEstadoTerminados():
    if len(terminados) == 0:
        return "-"
    resultado = ""
    for i in range(len(terminados)):
        resultado = resultado + terminados[i].nombre + " "
    return resultado

#-------------------------------------
#funcion que ordena los procesos en terminados de acuerdo al tiempo de llegada
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
#funcion que calcula el tiempo de espera promedio de la simulacion
def calculaEsperaPromedio():
    cantidad = len(terminados)
    suma = 0.0
    for i in range(cantidad):
        suma += terminados[i].tEspera
    return suma/cantidad

#-------------------------------------
#funcion que calcula del turnaround promedio de una simulacion
def calculaTurnaroundPromedio():
    cantidad = len(terminados)
    suma = 0.0
    for i in range(cantidad):
        suma += terminados[i].tEspera + terminados[i].tCPU
    return suma/cantidad

#-------------------------------------
#funcion que hace la simulacion de priority scheduling
#recibe como parametro un booleano que representa si la politica es expulsiva o no
def prioScheduling(isPreemptive):
    global enCPU
    for i in range(len(lineas)):
        words = lineas[i].split() #se divide la linea de la eentrada en palabras y se guardan en un arreglo
        
        #si se recibe el evento de llegada se valida el CPU y la cola de listos y se inserta el proceso en el lugar correspondiente
        if words[1] == 'Llega':
            nuevo = Proceso(words[2], words[4], int(words[0]))
            if len(listos) == 0 and enCPU is None:
                enCPU = nuevo
            else:
                insertaListos(nuevo, isPreemptive)
            print('Proceso ' + words[2] + ' creado' + ' en tiempo: ' + words[0])
            
        #si se recibe el evento de terminacion se valida si se termino el proceso del CPU
        elif words[1] == 'Acaba':
            #si si, se guarda en proceso del CPU y se carga el primero de la cola de listos
            if enCPU.nombre == words[2]:
                enCPU.tTermina = int(words[0])
                terminados.append(enCPU)
                enCPU = None
                if len(listos) > 0:
                    enCPU = listos.pop(0)
                    
            #si no, se saca el proceso de la cola donde se encuentre
            #en ambos casos el proceso se guarda en la lista de terminados
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
            
        #si se recibe el evento de iniciar I/O, primero se valida que el proceso este en el CPU y que no se encuentre ya en la cola de bloqueados
        #si se cumplen las dos validaciones, se pasa el proceso del CPU a la cola de bloqueados y se trae el siguiente proceso de la cola de listos
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
            
        #si se recibe el evento de terminar I/O se trae al proceso a la cola de listos y se coloca de nuevo en la cola de listos, en su lugar apropiado
        elif words[1] == 'endI/O':
            indiceBloqueados = buscaBloqueados(words[2])
            if indiceBloqueados == -1:
                print('El proceso no estaba bloqueado')
            else:
                insertaListos(bloqueados.pop(indiceBloqueados), isPreemptive)
            print('Proceso ' + words[2] + ' endI/O' + ' en tiempo: ' + words[0])

        #si se recibe un evento que no es reconocido por el simulador, este muestra un mensaje de error y no hace cambios en el estado del simulador, pero si transcurre el tiempo
        else:
            print('El simulador no reconoce el evento' + words[1])
        
        #despues de procesar el evento, se guarda el estado actual de las colas y el CPU
        guardarEstado(lineas[i])
        
        #se valida que la siguiente linea no sea la ultima
        if i+1 >= len(lineas):
            print('Se llegó al final de la entrada sin el evento de FinSimulación')
            break
        else: 
            #se valida si la siguiente linea marca el fin de la simulación
            if lineas[i+1].split()[1] != 'FinSimulacion':
                #si no, se calcula el tiempo transcurrido entre eventos y se le suma en el atributo apropiado a los procesos en la diferentes colas
                tiempo = int(lineas[i+1].split()[0]) - int(words[0])
                sumaListos(tiempo)
                sumaBloqueados(tiempo)
                sumaEnCPU(tiempo)
            #si si, se guarda el estado final y se termina la simulacion
            else:
                print(lineas[i+1].split()[0] + "\n")
                guardarEstado(lineas[i+1])
                break
            
    
    
#-------------------------------------
#sse checa el tipo de politica y se pasa el parametro apropiado al metodo de la simulacion
pCorrecta = False
if politica == "prioNonPreemptive":
    prioScheduling(False)
    pCorrecta = True
elif politica == "prioPreemptive":
    pCorrecta = True
    prioScheduling(True)
else:
    print("No se cubre esta politica: " + politica) #en caso que la politica no sea la esperada por el programa no se hace nada

if pCorrecta:
    esperaPromedio = calculaEsperaPromedio()
    turnaroundPromedio = calculaTurnaroundPromedio()
    arrTerminados = ordenarTerminados()
    
    headersEstados = ['Evento', 'Cola de listos', 'CPU', 'Procesos Bloqueados', 'Terminados']
    headersProcesos = ['Proceso', 'Tiempo de Llegada', 'Tiempo de Terminacion', 'Tiempo de CPU', 'Tiempo de Espera', 'Turnaround', 'Tiempo de I/O']
    
        
    print(tabulate(estados, headers=headersEstados)) #se imprime la tabla de estados
    print("\n")
    print(tabulate(arrTerminados, headers=headersProcesos)) #se imprime la tabla de procesos
    print("\n")
    print('Espera Promedio: ' + str(round(esperaPromedio, 2)))
    print('Turnaround Promedio: ' + str(round(turnaroundPromedio, 2)))