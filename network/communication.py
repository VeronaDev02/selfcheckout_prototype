import socket
import time
from queue import Queue

class Communication:
    def __init__(self):
        """
        Inicializa a classe Communication com as configurações de rede e a fila de mensagens.
        """
        self.IP_DVR = '192.168.101.250'
        self.PORTA_ENV_DVR = 38800
        self.LOCAL_IP = '0.0.0.0'
        self.LOCAL_PORT = 38800
        self.REMOTE_CONFIGS = [
            ('192.168.101.131', 8080, 8131, 'root1'),
            ('192.168.101.132', 8080, 8132, 'root2'),
            ('192.168.101.133', 8080, 8133, 'root3'),
            ('192.168.101.134', 8080, 8134, 'root4')
        ]
        self.message_queue = Queue()

    def send_text(self, data, ip_dvr, porta_env_dvr, porta_envio_local_dvr):
        """
        Envia texto para o DVR.

        :param data: O texto a ser enviado.
        :param ip_dvr: O endereço IP do DVR.
        :param porta_env_dvr: A porta de envio do DVR.
        :param porta_envio_local_dvr: A porta de envio local do DVR.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(('0.0.0.0', porta_envio_local_dvr))
            if isinstance(data, str):
                data = data.encode()
            sock.sendto(data, (ip_dvr, porta_env_dvr))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            sock.close()

    def listen_and_update(self):
        """
        Escuta mensagens e atualiza as janelas.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.LOCAL_IP, self.LOCAL_PORT))
            while True:
                time.sleep(1)
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')
                for remote_ip, remote_port, local_port, root in self.REMOTE_CONFIGS:
                    if addr[0] == remote_ip and addr[1] == remote_port:
                        self.send_text(data, self.IP_DVR, self.PORTA_ENV_DVR, local_port)
                        self.message_queue.put((root, message))
                        break

# Instância global da classe Communication
communication_instance = Communication()
message_queue = communication_instance.message_queue
