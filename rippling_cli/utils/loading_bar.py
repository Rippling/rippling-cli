import itertools
import sys
import threading
import time
from typing import Optional

import click


class LoadingBar(threading.Thread):
    """
    A loading bar that can be used to show progress of a long-running operation in the CLI.
    There are two types of loading bars:
        - Circular: A circular loading bar that spins while the operation is in progress.
        - Bar: A progress bar that fills up as the operation progresses.
    """
    def __init__(self, label: Optional[str] = None, char='#', loader: str = 'circular', length: int = 20,
                 stream=sys.stdout):
        super().__init__()
        self.label = label
        self.loader = loader
        self.char = char
        self.length = length
        self.stream = stream
        self.stop_event = threading.Event()

    def run(self):
        """
        Start the loading bar.
        :return:
        """
        if self.loader == 'circular':
            loader_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            loader_cycle = itertools.cycle(loader_frames)
            while not self.stop_event.is_set():
                progress = int(time.time() * 4) % (self.length + 1)
                bar = f"\r{self.label + ': ' if self.label else ''}{next(loader_cycle)}{' ' * (self.length - progress)}"
                self.stream.write(bar)
                self.stream.flush()
                time.sleep(0.1)
        elif self.loader == 'bar':
            while not self.stop_event.is_set():
                progress = int(time.time() * 4) % (self.length + 1)
                bar = f"\r{self.label + ': ' if self.label else ''}{self.char * progress:{self.length}}"
                self.stream.write(bar)
                self.stream.flush()
                time.sleep(0.1)

    def stop(self):
        """
        Stop the loading bar.
        :return:
        """
        self.stop_event.set()


def start_circular_loading_bar(length: int = 3) -> LoadingBar:
    """
    Start a circular loading bar with the specified length.
    :param length:
    :return:
    """
    loading_bar = LoadingBar(length=length, loader='circular')
    loading_bar.start()
    return loading_bar


def get_total_bar_length(loading_bar: LoadingBar) -> int:
    """
    Get the length of the loading bar.
    :param loading_bar:
    :return:
    """
    total_length = loading_bar.length
    if loading_bar.label:
        total_length += len(loading_bar.label) + 2
    return total_length


def stop_loading_bar(loading_bar: LoadingBar, success_message: Optional[str] = None):
    """
    Stop the loading bar, clear the loading bar and print the success message.
    :param loading_bar:
    :param success_message:
    :return:
    """
    loading_bar.stop()
    loading_bar.join()
    click.echo("\r" + " " * get_total_bar_length(loading_bar) + "\r", nl=False)  # Clear the line
    if success_message:
        click.echo(success_message)


def start_loading_bar(label: str, length: int = 20, char: str = '#') -> LoadingBar:
    """
    Start a progress bar with the specified label, length and character.
    :param label:
    :param length:
    :param char:
    :return:
    """
    loading_bar = LoadingBar(length=length, loader='bar', label=label, char=char)
    loading_bar.start()
    return loading_bar
