import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import collections
import time
import tracemalloc
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")


class CifradoCesar:
    def __init__(self):
        # Usamos un set para almacenar las palabras del texto original
        self.diccionario = set()

    def normalizar(self, char):
        # Función simple para quitar acentos y trabajar solo con el abecedario base
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ü': 'u', 'Ü': 'u'
        }
        return reemplazos.get(char, char)

    def ajustar_ascii(self, val):
        # Esta función hace el "wrap-around": si pasamos de 'z', volvemos a 'a'
        if val > 122: return val - 26  # Si es > 'z', le restamos 26
        if val < 97: return val + 26  # Si es < 'a', le sumamos 26
        return val

    def descifrar_texto(self, texto, salto):
        res = []
        for letra in texto:
            l_norm = self.normalizar(letra)
            if l_norm.isalpha():
                codigo = int(ord(l_norm))

                # Manejo especial de la ñ para que la rotación sea correcta
                if codigo == 241 or codigo == 209:
                    nuevo_cod = self.ajustar_ascii(110 - salto)
                else:
                    nuevo_cod = self.ajustar_ascii(codigo - salto)
                res.append(chr(nuevo_cod))
            else:
                # Si no es letra (espacio, coma, etc.), la dejamos igual
                res.append(letra)
        return "".join(res)

    def generar_caso(self, texto_original):
        self.diccionario.clear()
        # Generamos el diccionario de palabras válidas a partir del texto
        palabras = texto_original.split()
        for p in palabras:
            temp = ""
            for c in p:
                temp += self.normalizar(c)
            p_limpia = ''.join(filter(str.isalpha, temp)).lower()
            if len(p_limpia) > 1:
                self.diccionario.add(p_limpia)

        cifrado = []
        salto_real = random.randint(1, 25)  # El salto que debemos encontrar
        txt_min = texto_original.lower()

        for l in txt_min:
            l_norm = self.normalizar(l)
            if l_norm.isalpha():
                val = int(ord(l_norm))
                # Cifrado: Rotación a la derecha
                if val == 241 or val == 209:
                    val = self.ajustar_ascii(110 + salto_real)
                else:
                    val = self.ajustar_ascii(val + salto_real)
                cifrado.append(chr(val))
            else:
                cifrado.append(l)

        return "".join(cifrado), salto_real

    def medir_rendimiento(self, funcion, *args):
        # Wrapper para medir tiempo y memoria (tracemalloc)
        tracemalloc.start()
        t_inicio = time.perf_counter_ns()
        resultado = funcion(*args)
        t_final = time.perf_counter_ns()
        _, pico_memoria = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return resultado, t_final - t_inicio, pico_memoria

    # --- ALGORITMOS ---

    def fuerza_bruta(self, cifrado):
        resultados = []
        # Ciclo que prueba todas las 25 posibilidades
        for k in range(1, 26):
            intento = self.descifrar_texto(cifrado, k)
            resultados.append(f"Salto {k:02d}: {intento}")
        return resultados

    def divide_y_venceras(self, cifrado):
        # Muestreo: Si el texto es largo, solo tomamos una pequeña porción para analizar
        if len(cifrado) > 200:
            parte_analisis = cifrado[:100]  # Muestra constante de 100 caracteres
        else:
            parte_analisis = cifrado[:len(cifrado) // 2]  # Mitad si es corto

        mejor_salto = 0
        max_coincidencias = -1

        for k in range(1, 26):
            txt_temp = self.descifrar_texto(parte_analisis, k)  # Desciframos solo la muestra
            palabras = txt_temp.split()
            aciertos = 0
            for p in palabras:
                p_limpia = "".join(filter(str.isalpha, self.normalizar(p))).lower()
                # Verificamos si la palabra limpia está en nuestro diccionario
                if p_limpia in self.diccionario:
                    aciertos += 1
            if aciertos > max_coincidencias:
                max_coincidencias = aciertos
                mejor_salto = k  # Guardamos el salto con más aciertos

        # Aplicamos el salto ganador a TODO el texto una sola vez
        final = self.descifrar_texto(cifrado, mejor_salto)
        return [f"DyV encontró Salto {mejor_salto}: {final}"]

    def algoritmo_voraz(self, cifrado):
        # Paso 1: Contamos la frecuencia de letras (heurística)
        texto_limpio = "".join(filter(str.isalpha, cifrado.lower()))
        contador = collections.Counter(texto_limpio)
        if not contador: return ["Error: No hay letras"]

        top_letras = [x[0] for x in contador.most_common(3)]  # Las 3 más frecuentes
        candidatos = ['e', 'a', 'o']  # Las letras más comunes en español

        mejor_intento = "Fallo: No se detectó patrón"
        max_aciertos = 0

        # Mapeamos las letras más frecuentes del cifrado a las más frecuentes del español
        for letra_cif in top_letras:
            if ord(letra_cif) > 122: continue
            for meta in candidatos:
                dif = (ord(letra_cif) - ord(meta)) % 26
                if dif == 0: dif = 26

                # OPTIMIZACIÓN: Solo probamos con una muestra para validar el resultado
                muestra = cifrado[:150]
                prueba_muestra = self.descifrar_texto(muestra, dif)

                aciertos = 0
                for pal in prueba_muestra.split():
                    p_limpia = "".join(filter(str.isalpha, self.normalizar(pal))).lower()
                    if len(p_limpia) > 1 and p_limpia in self.diccionario:
                        aciertos += 1

                if aciertos > max_aciertos:
                    max_aciertos = aciertos
                    # Solo desciframos el texto completo si este es el mejor intento
                    txt_completo = self.descifrar_texto(cifrado, dif)
                    mejor_intento = f"Voraz (Salto {dif}): {txt_completo}"

        return [mejor_intento]

    def branch_and_bound(self, cifrado):
        # Funcion que calcula la puntuación (número de aciertos en el diccionario)
        def obtener_score(texto):
            palabras = texto.split()
            if not palabras: return 0
            aciertos = 0
            for p in palabras:
                clean = "".join(filter(str.isalpha, self.normalizar(p))).lower()
                if clean in self.diccionario:
                    aciertos += 1
            return aciertos

        scores = []
        # Usamos una muestra para calcular los scores
        muestra = cifrado[:150]

        # Precálculo: Obtenemos el puntaje de cada salto en la muestra
        for k in range(1, 26):
            txt = self.descifrar_texto(muestra, k)
            pts = obtener_score(txt)
            scores.append((k, pts))

        best_global = {'score': -1, 'salto': 0}

        # Funcion recursiva que aplica la lógica de Ramificación y Poda (B&B)
        def bb_recursivo(inicio, fin):
            max_local = -1
            # Calculamos la COTA (Bound): el mejor puntaje posible en el rango
            for i in range(inicio, fin):
                if scores[i][1] > max_local:
                    max_local = scores[i][1]

            # PODA: Si el potencial máximo (max_local) no mejora el mejor score global, se corta la rama
            if max_local <= best_global['score']:
                return

            # Caso Base: Si ya llegamos a un solo elemento (una sola clave)
            if fin - inicio == 1:
                k, pts = scores[inicio]
                if pts > best_global['score']:
                    best_global['score'] = pts
                    best_global['salto'] = k
                return

            # Ramificacion: Dividimos y llamamos a la recursión
            medio = (inicio + fin) // 2
            bb_recursivo(inicio, medio)
            bb_recursivo(medio, fin)

        bb_recursivo(0, 25)
        # Aplicamos el salto ganador una sola vez al texto completo
        final = self.descifrar_texto(cifrado, best_global['salto'])
        return [f"B&B Poda (Salto {best_global['salto']}): {final}"]


# ================= INTERFAZ =================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto Final - Comparativa Algoritmos")
        self.root.geometry("1000x800")
        self.logica = CifradoCesar()
        self.txt_actual = ""

        # Panel Superior
        frame_input = ttk.LabelFrame(self.root, text="Datos de Entrada")
        frame_input.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_input, text="Texto a Cifrar:").pack(anchor="w", padx=10)
        self.entrada = ttk.Entry(frame_input, width=80)
        self.entrada.pack(pady=10, padx=10)

        btn_cifrar = ttk.Button(frame_input, text="Generar Caso de Prueba", command=self.generar)
        btn_cifrar.pack(pady=5)

        self.lbl_status = ttk.Label(frame_input, text="Esperando datos...", foreground="blue")
        self.lbl_status.pack(pady=5)

        # Vista previa del cifrado
        ttk.Label(frame_input, text="Vista Previa del Cifrado Generado:", foreground="gray").pack(anchor="w", padx=5)
        self.vista_cifrado = scrolledtext.ScrolledText(frame_input, height=10, width=80)
        self.vista_cifrado.pack(pady=5, padx=5, fill="x")

        # Panel Botones
        frame_btns = ttk.LabelFrame(self.root, text="Ejecutar Algoritmo")
        frame_btns.pack(padx=10, pady=5, fill="x")

        box = ttk.Frame(frame_btns)
        box.pack(pady=10)

        ttk.Button(box, text="1. Fuerza Bruta", command=lambda: self.correr(1)).grid(row=0, column=0, padx=10)
        ttk.Button(box, text="2. Divide y Vencerás", command=lambda: self.correr(2)).grid(row=0, column=1, padx=10)
        ttk.Button(box, text="3. Voraz (Greedy)", command=lambda: self.correr(3)).grid(row=0, column=2, padx=10)
        ttk.Button(box, text="4. Branch & Bound", command=lambda: self.correr(4)).grid(row=0, column=3, padx=10)

        ttk.Separator(frame_btns, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(frame_btns, text="VER GRÁFICAS COMPARATIVAS", command=self.graficar).pack(pady=5, fill='x',
                                                                                             padx=50)

        # Panel Salida
        frame_out = ttk.LabelFrame(self.root, text="Salida y Métricas")
        frame_out.pack(padx=10, pady=10, fill="both", expand=True)

        self.txt_salida = scrolledtext.ScrolledText(frame_out, height=10)
        self.txt_salida.pack(fill="both", expand=True, padx=5, pady=5)

        self.lbl_metrics = ttk.Label(frame_out, text="Tiempo: 0 ns | Memoria: 0 bytes")
        self.lbl_metrics.pack(anchor="e", padx=10)

    def generar(self):
        texto = self.entrada.get()
        if not texto:
            messagebox.showwarning("Aviso", "Por favor escribe un texto primero.")
            return
        cifrado, salto = self.logica.generar_caso(texto)
        self.txt_actual = cifrado

        self.lbl_status.config(text=f"Proceso completado (Salto real: {salto})")

        self.vista_cifrado.delete(1.0, tk.END)
        self.vista_cifrado.insert(tk.END, cifrado)

        self.txt_salida.delete(1.0, tk.END)
        self.txt_salida.insert(tk.END, "Caso generado. Selecciona un algoritmo para descifrar.")

    def correr(self, op):
        if not self.txt_actual:
            messagebox.showerror("Error", "Primero genera el cifrado.")
            return
        self.txt_salida.delete(1.0, tk.END)
        res, t, m = None, 0, 0
        nombre = ""

        if op == 1:
            nombre = "Fuerza Bruta"
            res, t, m = self.logica.medir_rendimiento(self.logica.fuerza_bruta, self.txt_actual)
        elif op == 2:
            nombre = "Divide y Vencerás"
            res, t, m = self.logica.medir_rendimiento(self.logica.divide_y_venceras, self.txt_actual)
        elif op == 3:
            nombre = "Voraz"
            res, t, m = self.logica.medir_rendimiento(self.logica.algoritmo_voraz, self.txt_actual)
        elif op == 4:
            nombre = "Branch & Bound"
            res, t, m = self.logica.medir_rendimiento(self.logica.branch_and_bound, self.txt_actual)

        self.txt_salida.insert(tk.END, f"=== Resultado {nombre} ===\n")
        if isinstance(res, list):
            for linea in res:
                self.txt_salida.insert(tk.END, linea + "\n")
        else:
            self.txt_salida.insert(tk.END, str(res))
        self.lbl_metrics.config(text=f"Tiempo: {t} ns | Memoria Pico: {m} bytes")

    def graficar(self):
        if not self.txt_actual:
            messagebox.showerror("Error", "No hay datos.")
            return

        _, t1, m1 = self.logica.medir_rendimiento(self.logica.fuerza_bruta, self.txt_actual)
        _, t2, m2 = self.logica.medir_rendimiento(self.logica.divide_y_venceras, self.txt_actual)
        _, t3, m3 = self.logica.medir_rendimiento(self.logica.algoritmo_voraz, self.txt_actual)
        _, t4, m4 = self.logica.medir_rendimiento(self.logica.branch_and_bound, self.txt_actual)

        algos = ["F. Bruta", "DyV", "Voraz", "B&B"]
        tiempos = [t1, t2, t3, t4]
        mems = [m1, m2, m3, m4]

        top = tk.Toplevel(self.root)
        top.title("Comparativa de Rendimiento")
        top.geometry("900x500")
        fig = Figure(figsize=(10, 5), dpi=100)

        ax1 = fig.add_subplot(121)
        barras1 = ax1.bar(algos, tiempos, color='#6FA3D6')
        ax1.set_title('Tiempo (ns)')
        for b in barras1:
            h = b.get_height()
            ax1.text(b.get_x() + b.get_width() / 2, h, f'{int(h)}', ha='center', va='bottom', fontsize=8)

        ax2 = fig.add_subplot(122)
        barras2 = ax2.bar(algos, mems, color='#76D78E')
        ax2.set_title('Memoria (bytes)')
        for b in barras2:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width() / 2, h, f'{int(h)}', ha='center', va='bottom', fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = MainApp(ventana)
    ventana.mainloop()
