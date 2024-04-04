#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Universidade Tecnológica Federal do Paraná
#===============================================================================

import sys
import timeit
import numpy as np
import cv2

#===============================================================================

INPUT_IMAGE =  'arroz.bmp'

# TODO: ajuste estes parâmetros!
NEGATIVO = False
THRESHOLD = 0.8
ALTURA_MIN = 10
LARGURA_MIN = 10
N_PIXELS_MIN = 80

#===============================================================================

def binariza (img, threshold):
    
# Com np.where
    img_bin = np.where(img > THRESHOLD,1,0) # 0 e 1 pois a imagem está normalizada
    
    return(img_bin)

#-------------------------------------------------------------------------------

def inundar(x,y,rotulo,extremidades_Y, extremidades_X, img):
        
        print("Estamos no Rotulo: {}".format(rotulo))

        altura, largura = img.shape

    # Verificar se as coordenadas estão dentro dos limites da imagem
        if x < 0 or x >= largura or y < 0 or y >= altura:
            return
    
    # se o pixel já foi marcado ou não é igual a 1
        if img[y][x] != 1:
            return

    # Marcar o pixel
        img[y][x] = rotulo

        
        # Adicionando as coordenadas do pixel atual na lista

        extremidades_Y.append(y)
        extremidades_X.append(x)

        #Vizinhança 4
        inundar(x+1, y, rotulo, extremidades_Y, extremidades_X, img)  # Direita
        inundar(x, y+1, rotulo, extremidades_Y, extremidades_X, img)  # Baixo
        inundar(x-1, y, rotulo, extremidades_Y,extremidades_X, img)  # Esquerda
        inundar(x, y-1, rotulo, extremidades_Y, extremidades_X, img)  # Cima

        #Vizinhança 8 

        #inundar(x+1, y-1, rotulo,extremidades_Y, extremidades_X, img)  # Cima direita
        #inundar(x-1, y-1, rotulo,extremidades_Y, extremidades_X, img)  # Cima esquerda
        #inundar(x+1, y+1, rotulo,extremidades_Y, extremidades_X, img)  # Baixo esquerda
        #inundar(x-1, y+1, rotulo, extremidades_Y, extremidades_X, img)  # Baixo direita


def rotula (img, largura_min, altura_min, n_pixels_min):
    
    ##Vamos percorrer a imagem e rotular ela, depois vamos analizar as coordenadas dos pixels que foram armazenados.

    linhas, colunas = img.shape

    extremidades_X = [] # Listas que vao armazenar as coordenadas dos pixels do Blob
    extremidades_Y = []
    componentes = [] 
    
    rotulo = 1  

    for y in range(linhas):
        for x in range(colunas):
            if img[y][x] == 1:  # Verificar se o pixel é 1
                rotulo += 1 
                inundar(x,y,rotulo,extremidades_Y,extremidades_X, img) 

                ## Ainda na iteração, vamos veriricar as extremidades do blob que acabamos de rotular.

                n_pixels = len(extremidades_Y) * len(extremidades_X)
                T = min(extremidades_Y)  # topo é o minimo das coordenadas y
                L = min(extremidades_X) #  esquerda é o minimo do x
                B = max(extremidades_Y) # Maximo de Y é o pixel mais baixo
                R = max(extremidades_X) # Direita é o maximo do X

                if(n_pixels > n_pixels_min and (B - T) > altura_min and (R - L) > largura_min):
                    componentes.append({   # Coloca o dicionario com as informações do blob na lista.
                        'rotulo': rotulo,
                        'Numero de Pixels': n_pixels,
                        'T': T,
                        'L': L,
                        'B': B,
                        'R': R
                    })
            extremidades_Y.clear() #Depois de adicionado ao Dicionário, vamos limpar as listas para armazenar as coordenadas do proximo blob
            extremidades_X.clear()
            

    print("Lista de componentes: {}".format(componentes))
    return(componentes)



    '''Rotulagem usando flood fill. Marca os objetos da imagem com os valores
[0.1,0.2,etc].

Parâmetros: img: imagem de entrada E saída.
            largura_min: descarta componentes com largura menor que esta.
            altura_min: descarta componentes com altura menor que esta.
            n_pixels_min: descarta componentes com menos pixels que isso.

Valor de retorno: uma lista, onde cada item é um vetor associativo (dictionary)
com os seguintes campos:

'label': rótulo do componente.
'n_pixels': número de pixels do componente.
'T', 'L', 'B', 'R': coordenadas do retângulo envolvente de um componente conexo,
respectivamente: topo, esquerda, baixo e direita.'''

    # TODO: escreva esta função.
    # Use a abordagem com flood fill recursivo.

#===============================================================================

def main ():

    # Abre a imagem em escala de cinza.
    img = cv2.imread (INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    # É uma boa prática manter o shape com 3 valores, independente da imagem ser
    # colorida ou não. Também já convertemos para float32.
    img = img.reshape ((img.shape [0], img.shape [1], 1))
    img = img.astype (np.float32) / 255

    # Mantém uma cópia colorida para desenhar a saída.
    img_out = cv2.cvtColor (img, cv2.COLOR_GRAY2BGR)

    # Segmenta a imagem.
    if NEGATIVO:
        img = 1 - img

    img = binariza (img, THRESHOLD)
    
    img = cv2.convertScaleAbs(img) # A imagem estava com problema para exibir depois da binarização, mas o arquivo salvo estava exibindo corretamente a imagem binarizada
    
    cv2.imshow ('01 - binarizada', img*255)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite ('01 - binarizada.png', img*255)

    start_time = timeit.default_timer ()
    componentes = rotula (img, LARGURA_MIN, ALTURA_MIN, N_PIXELS_MIN)
    n_componentes = len (componentes)
    print ('Tempo: %f' % (timeit.default_timer () - start_time))
    print ('%d componentes detectados de acordo com os critérios.' % n_componentes)

    # Mostra os objetos encontrados.
    for c in componentes:
        cv2.rectangle (img_out, (c ['L'], c ['T']), (c ['R'], c ['B']), (0,0,1))

    cv2.imshow ('02 - out', img_out)
    cv2.imwrite ('02 - out.png', img_out*255)
    cv2.waitKey ()
    cv2.destroyAllWindows ()


if __name__ == '__main__':
    main ()

#===============================================================================
