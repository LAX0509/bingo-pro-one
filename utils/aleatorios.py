import time

class LibreriaAleatoria:
    def __init__(self, semilla=None):
        # [x] REQUERIMIENTO: Semilla con el reloj de la máquina
        self.xo = semilla if semilla else int(time.time() * 1000)
        self.a = 1103515245
        self.c = 12345
        self.m = 2**31

    def _generar_siguiente(self):
        self.xo = (self.a * self.xo + self.c) % self.m
        return self.xo / self.m

    def generar_entero(self, lim_inf, lim_sup):
        u = self._generar_siguiente()
        rango = (lim_sup + 1) - lim_inf
        return int(lim_inf + (u * rango))
    
    def generar_lista_unica(self, cantidad, lim_inf, lim_sup):
        numeros = []
        while len(numeros) < cantidad:
            n = self.generar_entero(lim_inf, lim_sup)
            if n not in numeros:
                numeros.append(n)
        return sorted(numeros)