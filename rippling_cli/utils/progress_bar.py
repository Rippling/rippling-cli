from contextlib import contextmanager

import click


@contextmanager
def report_progress(total_steps, label):
    """
    Report the progress of the steps and yield the progress callback.
    :param total_steps:
    :param label:
    :return:
    """
    with click.progressbar(length=total_steps, label=label, show_pos=True) as pbar:
        progress_callback = pbar.update

        try:
            yield progress_callback
        finally:
            pbar.update(total_steps)


def report_progress_steps(total_steps):
    """
    Report the progress of the steps.
    :param total_steps:
    :return:
    """
    steps_completed = 0
    while steps_completed < total_steps:
        yield steps_completed
        steps_completed += 1