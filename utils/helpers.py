from datetime import datetime

class CanvasHelper:
    def __init__(self, text_id_map, file_map):
        """
        Inicializa a classe CanvasHelper com os mapas de IDs de texto e arquivos.

        :param text_id_map: Mapeamento de IDs de texto para os canvas.
        :param file_map: Mapeamento de arquivos para os canvas.
        """
        self.text_id_map = text_id_map
        self.file_map = file_map

    def save_to_file(self, canvas, filename):
        """
        Salva o conteúdo do canvas em um arquivo.

        :param canvas: O canvas cujo conteúdo será salvo.
        :param filename: O nome do arquivo onde o conteúdo será salvo.
        """
        content = canvas.itemcget(self.text_id_map[canvas], "text")
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(filename, 'a') as file:
            file.write(f"{now}\n{content}\n")

    def update_text(self, canvas, text_id, message):
        """
        Atualiza o texto do canvas com a nova mensagem.

        :param canvas: O canvas cujo texto será atualizado.
        :param text_id: O ID do texto no canvas.
        :param message: A nova mensagem a ser exibida no canvas.
        """
        current_text = canvas.itemcget(text_id, "text")
        dataehora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # Verifica se a mensagem atual contém palavras específicas
        if any(keyword in message for keyword in ["PDV", "Trans", "Atend"]):
            print(f"Palavras identificadas na mensagem: {message}")
            # Salva o conteúdo da tela e reinicia a captura
            self.save_to_file(canvas, self.file_map[canvas])
            # Limpa o texto e adiciona a data e hora
            canvas.itemconfig(text_id, text=dataehora)
        else:
            # Atualiza o texto do canvas com a nova mensagem
            formatted_text = message.replace('^', '\n')
            updated_text = f"{current_text}\n{formatted_text}"
            canvas.itemconfig(text_id, text=updated_text)
        
        canvas.update_idletasks()
        
        # Ajuste da área de rolagem
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Rola para a parte inferior
        canvas.yview_moveto(1.0)
