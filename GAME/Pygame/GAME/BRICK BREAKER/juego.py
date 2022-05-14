import sys
import pygame
import time

ancho = 640
alto = 480
color_azul = (0,0,64) # Color azul para el fondo
color_blanco = (255,255,255) # color blanco, para textos


class Escena:
    "Esqueleto para cada una de las escenas del videojuego."
    def __init__(self):
        "Inicialización"
        self.proximaEscena = False
        self.jugando = True
    def leer_eventos(self,eventos):
        "Lee la lista de los eventos."
        pass

    def actualizar(self):
        "Cálculos y lógica."
        pass

    def dibujar(self):
        "Dibuja los objetos en pantalla."
        pass

    def cambiar_escena(self,escena):
        "Selecciona la nueva escena a ser desplegada"
        self.proximaEscena = escena

class Director:
    def __init__(self,titulo = " ", res = (ancho,alto)):
        pygame.init()   
        # inicializando pantalla
        self.pantalla = pygame.display.set_mode((res))
        #configurar nombre de la pantalla
        pygame.display.set_caption(titulo)
        # Crear Reloj
        self.reloj = pygame.time.Clock()
        self.escena = None
        self.escenas= {}

    def ejecutar(self,escena_inicial, fps=60):
        self.escena = self.escenas[escena_inicial]
        jugando = True
        while jugando:
            self.reloj.tick(fps)
            eventos = pygame.event.get()
            #revisar todos los eventos
            for evento in eventos:
                # si presiona la tachita de la barra de titulo
                if evento.type == pygame.QUIT:
                    # cerrar el videojuego
                    jugando = False

            self.escena.leer_eventos(eventos)
            self.escena.actualizar()
            self.escena.dibujar(self.pantalla)

            self.elegirEscena(self.escena.proximaEscena)

            if jugando:
                jugando = self.escena.jugando
        
            pygame.display.flip()

        time.sleep(3)

    def elegirEscena(self,proximaEscena):
        if proximaEscena:
            if proximaEscena not in self.escenas:
                self.agregarEscena(proximaEscena)
            self.escena = self.escenas[proximaEscena]
    
    def agregarEscena(self,escena):
        escenaClase = 'Escena'+ escena
        escenaObj = globals()[escenaClase]
        self.escenas[escena] = escenaObj();


class EscenaNivel1(Escena):
    def __init__(self):
        Escena.__init__(self)

        self.bolita = Bolita()
        self.jugador = Paleta()
        self.muro = Muro(112)

        self.puntuacion = 0
        self.vidas = 3
        self.esperando_saque = True
                    
        # Ajustar repeticion de evento de tecla presionada
        pygame.key.set_repeat(30)
    
    def leer_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < ancho/2:
                        self.bolita.speed = [3,-3]
                    else:
                        self.bolita.speed = [-3,-3]

    def actualizar(self):
        # Actualizar posición de la bolita
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop

        # colision entre bolita y jugador
        if pygame.sprite.collide_rect(self.bolita,self.jugador):
            self.bolita.speed[1] = -self.bolita.speed[1]

        # colision de la bolita con el muro
        lista = pygame.sprite.spritecollide(self.bolita,self.muro,False)
        if lista:
            ladrillo = lista[0]
            cx = self.bolita.rect.centerx
            if cx < ladrillo.rect.left or cx > ladrillo.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(ladrillo)
            self.puntuacion += 10

        # Revistar si bolita sale de la pantalla
        if self.bolita.rect.top  > alto:
            self.vidas -= 1
            self.esperando_saque = True
        
        if self.vidas <= 0:
            self.cambiar_escena('JuegoTerminado')

    def dibujar(self,pantalla):
          # Rellenar la pantalla
        pantalla.fill(color_azul)
        #mostrar puntuacion
        self.mostrar_puntuacion(pantalla)
        # mostrar vidas
        self.mostrar_vidas(pantalla)
        # dibujar bolita en pantalla
        pantalla.blit(self.bolita.image, self.bolita.rect)
        # dibujar jugador en pantalla
        pantalla.blit(self.jugador.image, self.jugador.rect)
        # Dibujar ladrillos
        self.muro.draw(pantalla)

    def mostrar_puntuacion(self,pantalla):
        fuente = pygame.font.SysFont('Consolas',20)
        texto  = fuente.render(str(self.puntuacion).zfill(5),True,color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topleft = [0,0]
        pantalla.blit(texto,texto_rect)

    def mostrar_vidas(self,pantalla):
        fuente = pygame.font.SysFont('Consolas',20)
        cadena = "Vidas " + str(self.vidas).zfill(2)
        texto  = fuente.render(str(cadena),True,color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [ancho,0]
        pantalla.blit(texto,texto_rect)

class EscenaJuegoTerminado(Escena):
    def actualizar(self):
        self.jugando = False

    def dibujar(self,pantalla):
        fuente = pygame.font.SysFont('Arial',72)
        texto  = fuente.render('GAME OVER',True,color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.center = [ancho/2,alto/2]
        pantalla.blit(texto,texto_rect)


class Bolita(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("Imagenes/Bolita.png")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        #posicion inicial centrada en pantalla
        self.rect.centerx = ancho /2
        self.rect.centery = alto /2
        # Establecer velocidad
        self.speed = [3,3]

    def update(self):
        # Evitar que salga por debajo
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        # Evitar que salga por la derecha
        elif self.rect.right >= ancho or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        # Mover en base a posicion actual y velocidad
        self.rect.move_ip(self.speed)

class Paleta(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("Imagenes/paleta.png")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        #posicion inicial centrada en pantalla en X
        self.rect.midbottom = (ancho /2, alto -20)
        # Establecer velocidad
        self.speed = [0,0]

    def update(self, evento):   
        # Buscar si se presiono la izquierda
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-6,0]
        elif evento.key == pygame.K_RIGHT and self.rect.right < ancho:
            self.speed = [6,0]
        else:
            self.speed = [0,0]
        # Mover en base a posicion actual y velocidad
        self.rect.move_ip(self.speed) 


class Ladrillo(pygame.sprite.Sprite):
    def __init__(self,posicion):
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("Imagenes/ladrillo.png")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        # posicion inicial, provista externamente
        self.rect.topleft = posicion

class Muro(pygame.sprite.Group):
    def __init__(self,cantidadLadrillos):
        pygame.sprite.Group.__init__(self)

        pos_x=0
        pos_y =20
        for i in range (cantidadLadrillos):
            ladrillo = Ladrillo((pos_x,pos_y))
            self.add(ladrillo)
            
            pos_x += ladrillo.rect.width
            if pos_x >= ancho:
                pos_x = 0
                pos_y += ladrillo.rect.height

director = Director('Juego de ladrillos',(ancho,alto))
director.agregarEscena('Nivel1')
director.ejecutar('Nivel1')













    


  
 

