import threading
from network.communication import communication_instance
from mouse_handler.mouse_events import mouse_handler_instance
from ui.interface import Interface

class MainApp:
    def __init__(self):
        """
        Inicializa a aplicação principal, configurando a interface e iniciando as threads.
        """
        self.interface = Interface.get_instance()
        self.start_threads()
        self.start_mainloop()

    def start_threads(self):
        """
        Inicia as threads para comunicação e manipulação de eventos do mouse.
        """
        threading.Thread(target=communication_instance.listen_and_update, daemon=True).start()
        threading.Thread(target=mouse_handler_instance.mouse_listener, daemon=True).start()

    def start_mainloop(self):
        """
        Inicia o loop principal da interface gráfica.
        """
        for root in [self.interface.root1, self.interface.root2, self.interface.root3, self.interface.root4]:
            root.after(100, self.interface.process_queue)
        self.interface.root1.mainloop()

if __name__ == "__main__":
    MainApp()
