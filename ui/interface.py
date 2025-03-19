import tkinter as tk
from screeninfo import get_monitors
from common.config import config_instance
from utils.helpers import CanvasHelper
from network.communication import communication_instance
import time

class Interface:
    _instance = None

    def __init__(self):
        """
        Inicializa a interface gráfica, configurando monitores, janelas, canvas e textos.
        """
        if Interface._instance is not None:
            raise Exception("Esta classe é um singleton!")
        else:
            Interface._instance = self

        self.monitors = get_monitors()
        self.setup_monitors()
        self.setup_windows()
        self.setup_canvas()
        self.setup_text()
        self.setup_bindings()
        self.intervalo_piscar = 1000
        self.painted_width = self.monitor_width // 5
        self.painted_height = self.monitor_height // 2
        self.canvas_helper = CanvasHelper(self.text_id_map, self.file_map)
        self.process_queue()

    @staticmethod
    def get_instance():
        """
        Retorna a instância singleton da classe Interface.

        :return: Instância da classe Interface.
        """
        if Interface._instance is None:
            Interface()
        return Interface._instance

    def setup_monitors(self):
        """
        Configura os monitores primário e secundário com base nas configurações.
        """
        if len(self.monitors) < 2:
            self.primary_monitor = self.monitors[0]
            self.secondary_monitor = self.monitors[0]
        else:
            self.primary_monitor = self.monitors[0]
            self.secondary_monitor = self.monitors[1]

        self.primary_monitor_width = self.primary_monitor.width
        self.primary_monitor_height = self.primary_monitor.height
        self.primary_monitor_offset_x = self.primary_monitor.x
        self.primary_monitor_offset_y = self.primary_monitor.y

        self.secondary_monitor_width = self.secondary_monitor.width
        self.secondary_monitor_height = self.secondary_monitor.height
        self.secondary_monitor_offset_x = self.secondary_monitor.x
        self.secondary_monitor_offset_y = self.secondary_monitor.y

        if config_instance.monitor_to_use == 1 or len(self.monitors) < 2:
            self.monitor_width = self.primary_monitor_width
            self.monitor_height = self.primary_monitor_height
            self.monitor_offset_x = self.primary_monitor_offset_x
            self.monitor_offset_y = self.primary_monitor_offset_y
        else:
            self.monitor_width = self.secondary_monitor_width
            self.monitor_height = self.secondary_monitor_height
            self.monitor_offset_x = self.secondary_monitor_offset_x
            self.monitor_offset_y = self.secondary_monitor_offset_y

        self.canto_inferior_direito_x = self.monitor_offset_x + self.monitor_width
        self.canto_inferior_direito_y = self.monitor_offset_y + self.monitor_height

        self.centro_x = self.canto_inferior_direito_x - (self.monitor_width // 2)
        self.centro_y = self.canto_inferior_direito_y - (self.monitor_height // 2)

    def setup_windows(self):
        """
        Configura as janelas principais da interface.
        """
        self.root1 = tk.Tk()
        self.root2 = tk.Tk()
        self.root3 = tk.Tk()
        self.root4 = tk.Tk()

        self.configure_window(self.root1, self.monitor_offset_x, 0, self.monitor_width // 5, self.monitor_height // 2)
        self.configure_window(self.root2, self.monitor_offset_x, self.monitor_height // 2, self.monitor_width // 5, self.monitor_height // 2)
        right_half_x = self.monitor_offset_x + (self.monitor_width // 2)
        self.configure_window(self.root3, right_half_x, 0, self.monitor_width // 5, self.monitor_height // 2)
        self.configure_window(self.root4, right_half_x, self.monitor_height // 2, self.monitor_width // 5, self.monitor_height // 2)

    def configure_window(self, root, x, y, width, height):
        """
        Configura uma janela específica com as dimensões e posição fornecidas.

        :param root: A janela a ser configurada.
        :param x: Posição X da janela.
        :param y: Posição Y da janela.
        :param width: Largura da janela.
        :param height: Altura da janela.
        """
        root.attributes('-topmost', True)
        root.attributes('-alpha', 0.9)
        root.overrideredirect(True)
        root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_canvas(self):
        """
        Configura os canvas para cada janela.
        """
        self.canvas1 = self.create_canvas(self.root1, self.monitor_width // 5, self.monitor_height // 2)
        self.canvas2 = self.create_canvas(self.root2, self.monitor_width // 5, self.monitor_height // 2)
        self.canvas3 = self.create_canvas(self.root3, self.monitor_width // 5, self.monitor_height // 2)
        self.canvas4 = self.create_canvas(self.root4, self.monitor_width // 5, self.monitor_height // 2)

    def create_canvas(self, root, width, height):
        """
        Cria um canvas em uma janela específica.

        :param root: A janela onde o canvas será criado.
        :param width: Largura do canvas.
        :param height: Altura do canvas.
        :return: O canvas criado.
        """
        canvas = tk.Canvas(root, width=width, height=height, bg='black')
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind("<Configure>", lambda e: self.on_canvas_configure(canvas))
        return canvas

    def setup_text(self):
        """
        Configura os textos iniciais para cada canvas.
        """
        self.text_id1 = self.create_text(self.canvas1, self.monitor_width // 5, self.monitor_height // 2)
        self.text_id2 = self.create_text(self.canvas2, self.monitor_width // 5, self.monitor_height // 2)
        self.text_id3 = self.create_text(self.canvas3, self.monitor_width // 5, self.monitor_height // 2)
        self.text_id4 = self.create_text(self.canvas4, self.monitor_width // 5, self.monitor_height // 2)

        self.text_id_map = {
            self.canvas1: self.text_id1,
            self.canvas2: self.text_id2,
            self.canvas3: self.text_id3,
            self.canvas4: self.text_id4
        }

        self.file_map = {
            self.canvas1: "screen1_log.txt",
            self.canvas2: "screen2_log.txt",
            self.canvas3: "screen3_log.txt",
            self.canvas4: "screen4_log.txt"
        }

        self.last_message_time = {
            self.canvas1: None,
            self.canvas2: None,
            self.canvas3: None,
            self.canvas4: None
        }

    def create_text(self, canvas, width, height):
        """
        Cria um texto em um canvas específico.

        :param canvas: O canvas onde o texto será criado.
        :param width: Largura do canvas.
        :param height: Altura do canvas.
        :return: O ID do texto criado.
        """
        return canvas.create_text(width // 2, height // 2, text="********************", font=("Helvetica", 8), fill="white", anchor=tk.CENTER, width=width)

    def setup_bindings(self):
        """
        Configura os eventos de fechamento para as janelas.
        """
        for root in [self.root1, self.root2, self.root3, self.root4]:
            self.bind_close_event(root)

    def bind_close_event(self, root):
        """
        Vincula o evento de fechamento à tecla Escape.

        :param root: A janela onde o evento será vinculado.
        """
        root.bind('<Escape>', lambda e: config_instance.close_window(self.root1, self.root2, self.root3, self.root4))

    def on_canvas_configure(self, canvas):
        """
        Atualiza a área de rolagem do canvas quando ele é redimensionado.

        :param canvas: O canvas a ser atualizado.
        """
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(1.0)

    def parar_piscar_janela(self, canvas, cor_original):
        """
        Para o efeito de piscar da janela e restaura a cor original.

        :param canvas: O canvas a ser atualizado.
        :param cor_original: A cor original do canvas.
        """
        canvas.configure(bg=cor_original)
        canvas.itemconfig(self.text_id_map[canvas], fill="white")

    def piscar_janela(self, canvas, cor_original, cor_alerta, root, mensagem_exibida):
        """
        Alterna a cor do canvas para criar um efeito de piscar.

        :param canvas: O canvas a ser atualizado.
        :param cor_original: A cor original do canvas.
        :param cor_alerta: A cor de alerta do canvas.
        :param root: A janela raiz.
        :param mensagem_exibida: Indica se a mensagem de alerta está sendo exibida.
        """
        def alternar_cor():
            if not mensagem_exibida:  # Verifica se a mensagem de tempo sem eventos excedido está sendo exibida
                return

            if canvas['bg'] == cor_original:
                canvas.configure(bg=cor_alerta)
                canvas.itemconfig(self.text_id_map[canvas], fill="black")
            else:
                canvas.configure(bg=cor_original)
                canvas.itemconfig(self.text_id_map[canvas], fill="white")
            
            root.after(self.intervalo_piscar, alternar_cor)

        alternar_cor()

    def move_and_resize_window(self, window, position, width, monitor_height, is_original_size):
        """
        Move e redimensiona uma janela específica.

        :param window: A janela a ser movida e redimensionada.
        :param position: A posição da janela.
        :param width: A largura da janela.
        :param monitor_height: A altura do monitor.
        :param is_original_size: Indica se a janela deve ser redimensionada para o tamanho original.
        """
        if not is_original_size:
            width += 230  # Adiciona 230 pixels ao width
            font_size = 16
            text_width = width * 2
        else:
            font_size = 8
            text_width = width
        
        window.geometry(f"{width}x{monitor_height}+{position[0]}+{position[1]}")

        # Atualiza o tamanho da fonte e o texto
        for canvas, text_id in self.text_id_map.items():
            canvas.itemconfig(text_id, font=("Helvetica", font_size), width=text_width, anchor=tk.CENTER)
            canvas.coords(text_id, width // 2, monitor_height // 2)

    def verificar_evento(self, canvas, root, ultima_atualizacao_evento, mensagem_exibida, verificar_evento_id):
        """
        Verifica se houve um evento recente e atualiza a janela de acordo.

        :param canvas: O canvas a ser atualizado.
        :param root: A janela raiz.
        :param ultima_atualizacao_evento: O timestamp da última atualização do evento.
        :param mensagem_exibida: Indica se a mensagem de alerta está sendo exibida.
        :param verificar_evento_id: O ID do evento de verificação.
        """
        if time.time() - ultima_atualizacao_evento > config_instance.tempoatencao and not mensagem_exibida:
            root.after(0, lambda: self.piscar_janela(canvas, 'black', 'yellow', root, mensagem_exibida))
            mensagem_exibida = True
        else:
            verificar_evento_id = root.after(100, lambda: self.verificar_evento(canvas, root, ultima_atualizacao_evento, mensagem_exibida, verificar_evento_id))

    def parar_processamento_anterior(self, root, verificar_evento_id):
        """
        Para o processamento anterior de eventos.

        :param root: A janela raiz.
        :param verificar_evento_id: O ID do evento de verificação.
        """
        if verificar_evento_id:
            root.after_cancel(verificar_evento_id)

    def process_message(self, window, message, canvas, root, ultima_atualizacao_evento, mensagem_exibida, verificar_evento_id, monitorar, last_message):
        """
        Processa uma mensagem recebida e atualiza o canvas correspondente.

        :param window: A janela onde a mensagem será exibida.
        :param message: A mensagem a ser processada.
        :param canvas: O canvas a ser atualizado.
        :param root: A janela raiz.
        :param ultima_atualizacao_evento: O timestamp da última atualização do evento.
        :param mensagem_exibida: Indica se a mensagem de alerta está sendo exibida.
        :param verificar_evento_id: O ID do evento de verificação.
        :param monitorar: Indica se a janela deve ser monitorada.
        :param last_message: A última mensagem processada.
        """
        ultima_atualizacao_evento = time.time()
        if last_message != message:
            last_message = message
            self.parar_processamento_anterior(root, verificar_evento_id)
        self.canvas_helper.update_text(canvas, self.text_id_map[canvas], message)    

        if mensagem_exibida:
            self.parar_piscar_janela(canvas, 'black')
            mensagem_exibida = False

        if any(keyword in message for keyword in ["PDV", "Atend", "Trans"]):
            monitorar = True

        if not any(keyword in message for keyword in ["Relatorio", "Gerencial"]) and monitorar:
            verificar_evento_id = root.after(0, lambda: self.verificar_evento(canvas, root, ultima_atualizacao_evento, mensagem_exibida, verificar_evento_id))
        else:
            monitorar = False

    def process_queue(self):
        """
        Processa a fila de mensagens e atualiza as janelas correspondentes.
        """
        while not communication_instance.message_queue.empty():
            window, message = communication_instance.message_queue.get()
            
            if window == 'root1':
                self.process_message(window, message, self.canvas1, self.root1, None, None, None, None, None)
            elif window == 'root2':
                self.process_message(window, message, self.canvas2, self.root2, None, None, None, None, None)
            elif window == 'root3':
                self.process_message(window, message, self.canvas3, self.root3, None, None, None, None, None)
            elif window == 'root4':
                self.process_message(window, message, self.canvas4, self.root4, None, None, None, None, None)
                    
        self.root1.after(100, self.process_queue)

if __name__ == "__main__":
    Interface()
