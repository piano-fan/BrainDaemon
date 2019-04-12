from subprocess import Popen, PIPE
import threading
import time


class Brain:
    def __init__(self, exec_path, on_stdout, on_stderr=None, on_shutdown=None):
        self.__on_stdout = on_stdout
        self.__on_stderr = on_stderr
        self.__on_shutdown = on_shutdown

        self.__splink = Popen([exec_path], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.__stdout_thread = threading.Thread(target=lambda: self.__listen_stdout())
        self.__stderr_thread = threading.Thread(target=lambda: self.__listen_stderr())
        self.__stdout_thread.start()
        self.__stderr_thread.start()

    def __listen_stdout(self):
        while True:
            text = self.__splink.stdout.readline().decode().rstrip()
            if text:
                self.__on_stdout(text)

            code = self.exit_code()
            if code is not None:
                if self.__on_shutdown:
                    self.__on_shutdown(code)
                break
            time.sleep(0.01)

    def __listen_stderr(self):
        while True:
            text = self.__splink.stderr.readline().decode().rstrip()
            if text:
                if self.__on_stderr:
                    self.__on_stderr(text)

            code = self.exit_code()
            if code is not None:
                break

    def exit_code(self):
        return self.__splink.poll()

    def send_message(self, text):
        self.__splink.stdin.write((text + "\n").encode())
        self.__splink.stdin.flush()

    def shutdown(self):
        self.send_message('end')
        self.__stdout_thread.join()
        self.__stderr_thread.join()

    def kill(self):
        self.__splink.kill()