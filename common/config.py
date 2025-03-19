import signal
import sys

class Config:
    def __init__(self):
        """
        Inicializa a classe Config com as configurações padrão e configura o manipulador de sinal.
        """
        self.tempoatencao = 8
        self.monitor_to_use = 2  # 1 para monitor primário, 2 para monitor secundário
        signal.signal(signal.SIGINT, self.signal_handler)

    def close_window(self, *roots):
        """
        Fecha as janelas e encerra o programa.

        :param roots: As janelas a serem fechadas.
        """
        for root in roots:
            root.quit()
        sys.exit(0)

    def signal_handler(self, sig, frame):
        """
        Manipulador de sinal para encerrar o programa.

        :param sig: O sinal recebido.
        :param frame: O frame atual.
        """
        from ui.interface import Interface
        interface = Interface.get_instance()
        self.close_window(interface.root1, interface.root2, interface.root3, interface.root4)

# Instância global da classe Config
config_instance = Config()
tempoatencao = config_instance.tempoatencao
monitor_to_use = config_instance.monitor_to_use
close_window = config_instance.close_window
