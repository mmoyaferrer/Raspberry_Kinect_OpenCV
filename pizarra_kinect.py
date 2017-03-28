# coding: utf-8
import freenect
import cv2
import numpy
import sys

pVez=True
imagenGuardada=0
pizarraMod=0
centroDelPuntoInicial=0
radio=0
threshold = 100
current_depth = 0
prev = None

cv2.namedWindow('Original')
cv2.namedWindow('Mapa')
cv2.namedWindow('Pizarra')
tilt = 0

# Métodos para el dibujado en la pizarra 

def ejecutarPizarra():
    global pVez
    global imagenGuardada
    global pizarraMod
    global centroDelPuntoInicial
    global radio
    global ultimo
    
    if pVez==True:
        ultimo=(0, 0)
        radio=1
        centroDelPuntoInicial=(-1,-1)
        pizarra=cv2.imread('pizarra.jpg',0)
        pizarraMod=pizarra
        imagenGuardada=pizarra
        
        imagenFlip=cv2.flip(pizarraMod,1)
        cv2.imshow('Pizarra',imagenFlip)
        
        pVez=False

def pararPizarra():
    ejecutando=False

def guardarImagenModificada(imagen):
    imagenGuardada=imagen
    
def obtenerImagenGuardada():
    return imagenGuardada

def limpiar_pizarra():
    global imagenGuardada
    global pizarraMod
  
    pizarra=cv2.imread('pizarra.jpg',0)
    pizarraMod=pizarra
    imagenGuardada=pizarra
    guardarImagenModificada(pizarraMod)
    

def actualizarPizarra(centro,grosor):
    global ultimo
    global radio
    radio=grosor
    (x, y) = centro
    (x0, y0) = ultimo
    x=x*0.3+ x0*0.7
    y=y*0.3+ y0*0.7
    centroDelPuntoInicial=(int(x),int(y))
    ultimo=centroDelPuntoInicial
    pizarraMod=obtenerImagenGuardada()
    cv2.circle(pizarraMod, centroDelPuntoInicial,radio,(0, 0, 0),thickness=5)

    imagenFlip=cv2.flip(pizarraMod,1)
    cv2.imshow('Pizarra',imagenFlip)
    guardarImagenModificada(pizarraMod)

def cambiar_grosor(valor):
    global radio
    radio = valor

# Métodos de MIDINect

def change_tilt(value):
    global tilt
    tilt = value

def change_threshold(value):
    global threshold
    threshold = value


def change_depth(value):
    global current_depth
    current_depth = value


def show_depth(dev, data, timestamp):
    global threshold
    global current_depth
    global prev

    actual = data

    if prev is None:
        prev = numpy.array(actual)

    source = (actual + prev) / 2

    prev = actual

    depth = 255 * numpy.logical_and(
            source >= current_depth - threshold,
            source <= current_depth + threshold)


    source += 1
    source >>= 3
    depth = depth.astype(numpy.uint8)
    source = source.astype(numpy.uint8)

    imagenFlip=cv2.flip(depth,1)
    cv2.imshow('Mapa', imagenFlip)

    draw_convex_hull(depth, source)

    if cv2.waitKey(10) == 27:
        sys.exit()


def draw_convex_hull(a, original):
    global radio
    original = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)

    ret, b = cv2.threshold(a, 255, 255, cv2.THRESH_BINARY)

    contornos, jerarquia = cv2.findContours(a,
            cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

    for n, cnt in enumerate(contornos):

        hull = cv2.convexHull(cnt)
        foo = cv2.convexHull(cnt, returnPoints=False)
        cv2.drawContours(original, contornos, n, (0, 35, 245))
        if len(cnt) > 3 and len(foo) > 2:
            defectos = cv2.convexityDefects(cnt, foo)
            if defectos is not None:
                defectos = defectos.reshape(-1, 4)
                puntos = cnt.reshape(-1, 2)
                #for d in defectos:
                    #if d[3] > 20:
                        #cv2.circle(original, tuple(puntos[d[0]]), 5, (255, 255, 0), 2)
                        #cv2.circle(original, tuple(puntos[d[1]]), 5, (255, 255, 0), 2)
                        #cv2.circle(original, tuple(puntos[d[2]]), 5, (0, 0, 255), 2)
                        


        lista = numpy.reshape(hull, (1, -1, 2))
        #cv2.polylines(original, lista, True, (255, 255, 255), 3)
        (x,y), radius = cv2.minEnclosingCircle(cnt)
        center=(x,y)
        center = tuple(map(int, center))
        radius = int(radius)
        cv2.circle(original, center, radius, (255, 0, 0), 3)
        actualizarPizarra(center,radio)
        print(center)
        
        if((x,y)<(x,50)):
            aux=tilt+1
            change_tilt(aux)
            print ("Subir")
        if ((x,y)>(x,450)):
            aux=tilt-1
            change_tilt(aux)
            print ("Bajar")

    imagenFlip=cv2.flip(original,1)
    cv2.imshow('Original', imagenFlip)

cv2.createTrackbar('Umbral', 'Original', threshold,     500,  change_threshold)
cv2.createTrackbar('Profundidad',     'Original', current_depth, 2048, change_depth)
cv2.createTrackbar('Inclinación', 'Original', 0, 30, change_tilt)
cv2.createTrackbar('Grosor trazo','Original',1,10,cambiar_grosor)
#cv2.createButton("Limpiar Pizarra")

def main(dev, ctx):
    ejecutarPizarra() # Creamos la ventana y la pizarra nada más lanzar el script.
    freenect.set_tilt_degs(dev, tilt)


freenect.runloop(depth=show_depth, body=main)

