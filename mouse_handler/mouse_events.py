from pynput import mouse
import time
from ui.interface import Interface
from common.config import monitor_to_use
import pyautogui

class MouseHandler:
    DOUBLE_CLICK_INTERVAL = 0.5
    ORIGINAL_FONT_SIZE = 5

    def __init__(self):
        """
        Inicializa a classe MouseHandler e configura o estado inicial.
        """
        self.last_click_time = 0
        self.last_click_position = (0, 0)
        self.janelas_ocultas = False
        self.last_quadrant = None
        self.saved_quadrant = None
        self.interface = Interface.get_instance()

    def get_quadrant(self, x, y, monitor_width, monitor_height):
        """
        Determina o quadrante com base na posição do clique.

        :param x: Posição X do clique.
        :param y: Posição Y do clique.
        :param monitor_width: Largura do monitor.
        :param monitor_height: Altura do monitor.
        :return: O quadrante correspondente à posição do clique.
        """
        if x < monitor_width / 2:
            return 1 if y < monitor_height / 2 else 3  # Quadrante 1 (superior esquerdo) ou 3 (inferior esquerdo)
        else:
            return 2 if y < monitor_height / 2 else 4  # Quadrante 2 (superior direito) ou 4 (inferior direito)

    def restore_windows(self):
        """
        Restaura todas as janelas para suas posições e tamanhos originais.
        """
        for root in [self.interface.root1, self.interface.root2, self.interface.root3, self.interface.root4]:
            root.deiconify()
        
        monitor_offset_x = self.interface.primary_monitor_offset_x if monitor_to_use == 1 else self.interface.secondary_monitor_offset_x
        monitor_width = self.interface.primary_monitor_width if monitor_to_use == 1 else self.interface.secondary_monitor_width
        right_half_x = monitor_offset_x + (monitor_width // 2)
        
        self.interface.move_and_resize_window(self.interface.root1, (monitor_offset_x, 0), self.interface.painted_width, self.interface.painted_height, is_original_size=True)
        self.interface.move_and_resize_window(self.interface.root2, (monitor_offset_x, self.interface.painted_height), self.interface.painted_width, self.interface.painted_height, is_original_size=True)
        self.interface.move_and_resize_window(self.interface.root3, (right_half_x, 0), self.interface.painted_width, self.interface.painted_height, is_original_size=True)
        self.interface.move_and_resize_window(self.interface.root4, (right_half_x, self.interface.painted_height), self.interface.painted_width, self.interface.painted_height, is_original_size=True)
        
        self.janelas_ocultas = False
        self.saved_quadrant = None

    def hide_windows_by_quadrant(self, quadrant):
        """
        Oculta janelas com base no quadrante.

        :param quadrant: O quadrante cujas janelas serão ocultadas.
        """
        for root in [self.interface.root1, self.interface.root2, self.interface.root3, self.interface.root4]:
            root.withdraw()
        
        if quadrant == 1:
            self.interface.root1.deiconify()
        elif quadrant == 3:
            self.interface.root2.deiconify()
        elif quadrant == 2:
            self.interface.root3.deiconify()
        elif quadrant == 4:
            self.interface.root4.deiconify()
        
        self.janelas_ocultas = True
        self.last_quadrant = quadrant
        self.saved_quadrant = quadrant

        # Ajusta a posição e o tamanho da janela visível para a posição de root1
        visible_windows = [root for root in [self.interface.root1, self.interface.root2, self.interface.root3, self.interface.root4] if root.state() == 'normal']
        
        if len(visible_windows) == 1:
            root1_geom = self.interface.root1.geometry().split('+')
            x = int(root1_geom[1])
            y = int(root1_geom[2])
            monitor_height = self.interface.primary_monitor_height if monitor_to_use == 1 else self.interface.secondary_monitor_height
            self.interface.move_and_resize_window(visible_windows[0], (x, y), self.interface.painted_width, monitor_height, is_original_size=False)

    def update_windows_visibility(self, monitor, quadrant):
        """
        Atualiza a visibilidade das janelas com base no estado atual.

        :param monitor: O monitor onde as janelas estão sendo exibidas.
        :param quadrant: O quadrante cujas janelas serão atualizadas.
        """
        if self.janelas_ocultas:
            self.restore_windows()
        else:
            self.hide_windows_by_quadrant(quadrant)

    def on_click(self, x, y, button, pressed):
        """
        Manipula eventos de clique do mouse.

        :param x: Posição X do clique.
        :param y: Posição Y do clique.
        :param button: O botão do mouse que foi clicado.
        :param pressed: Indica se o botão foi pressionado.
        """
        if pressed and button == mouse.Button.left:
            current_time = time.time()

            if current_time - self.last_click_time <= self.DOUBLE_CLICK_INTERVAL:
                monitor, monitor_width, monitor_height = (
                    (self.interface.primary_monitor, self.interface.primary_monitor_width, self.interface.primary_monitor_height) if monitor_to_use == 1 else
                    (self.interface.secondary_monitor, self.interface.secondary_monitor_width, self.interface.secondary_monitor_height)
                )
                
                quadrant = self.saved_quadrant if self.janelas_ocultas else self.get_quadrant(x - monitor.x, y - monitor.y, monitor_width, monitor_height)
                
                print(f'Duplo clique detectado na posição: ({x}, {y}) no monitor {"1" if monitor == self.interface.primary_monitor else "2"} no quadrante {quadrant}')
                
                self.interface.root1.after(0, self.update_windows_visibility, monitor, quadrant)
                
                self.last_click_time = 0
            else:
                self.last_click_time = current_time
                self.last_click_position = (x, y)

    def mouse_listener(self):
        """
        Configura o listener para o mouse.
        """
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

# Instância global da classe MouseHandler
mouse_handler_instance = MouseHandler()
