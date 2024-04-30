import os
import signal
import subprocess


class FlaskServer:
    """
    Class to manage the Flask server for local development by starting the server and stopping it.
    """
    def __init__(self, debug=None, port=5000):
        self.debug = debug
        self.port = port
        self.process = None

    def start(self):
        """
        Start the Flask server.
        :return:
        """
        env = os.environ.copy()
        env["FLASK_APP"] = "flux_dev_tools.server.flask"
        flask_command = ["python", "-m", "flask", "run", "--port", str(self.port)]
        if self.debug:
            flask_command.append("--debug")
        self.process = subprocess.Popen(flask_command, env=env, preexec_fn=os.setsid)
        return self.process
    def stop(self):
        """
        Stop the Flask server.
        :return:
        """
        if self.process:
            try:
                # Send the signal to the entire process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

                # Wait for the process to terminate
                self.process.wait(timeout=5)

                # If the process is still running after 5 seconds, kill it
                if self.process.poll() is None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except subprocess.TimeoutExpired:
                # If the process times out, kill it
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)

            # Close any open file descriptors associated with the process
            for fd in [self.process.stdin, self.process.stdout, self.process.stderr]:
                if fd is not None:
                    fd.close()