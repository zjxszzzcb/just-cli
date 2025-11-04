"""
Unified progress bar interface with automatic fallback between Rich and simple text implementations.
"""

import sys
from typing import Optional, Iterator, Any, Union
from abc import ABC, abstractmethod


class ProgressBarBase(ABC):
    """Base class for progress bars"""

    def __init__(self, iterable=None, total=None, desc="", unit="it", **kwargs):
        self.iterable = iterable
        self.total = total or (len(iterable) if iterable else 100)
        self.desc = desc
        self.unit = unit
        self.n = 0
        self.closed = False

    def __iter__(self) -> Iterator[Any]:
        if self.iterable is None:
            raise TypeError("Must provide iterable to iterate over")
        for obj in self.iterable:
            yield obj
            self.update(1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def update(self, n: int = 1) -> None:
        """Update progress by n steps"""
        if not self.closed:
            self.n += n
            self.display()

    def start(self) -> None:
        """Start the progress bar"""
        pass

    def close(self) -> None:
        """Close the progress bar"""
        self.closed = True

    def refresh(self) -> None:
        """Refresh the progress bar display (safe implementation)"""
        try:
            self.display()
        except Exception:
            pass

    @abstractmethod
    def display(self) -> None:
        """Display current progress"""
        pass


class RichProgressBar(ProgressBarBase):
    """Rich progress bar implementation"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._progress = None
        self._task = None

    def start(self) -> None:
        try:
            from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn
            self._progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=None),
                TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
                TextColumn("•"),
                DownloadColumn(binary_units=True) if self.unit in ["b", "bytes"] else TextColumn("[progress.download]{task.completed:>8.1f}/{task.total:>8.1f} {task.fields[unit]}"),
                TextColumn("•"),
                TimeRemainingColumn(),
            )
            self._task = self._progress.add_task(
                self.desc,
                total=self.total,
                unit=self.unit
            )
            self._progress.start()
        except Exception as e:
            # Fallback to simple progress bar if Rich fails
            self.__class__ = SimpleProgressBar
            self.__init__(self.iterable, self.total, self.desc, self.unit)
            self.start()

    def update(self, n: int = 1) -> None:
        if hasattr(self, '_progress') and self._progress and hasattr(self, '_task') and self._task is not None and not self.closed:
            try:
                self._progress.update(self._task, advance=n)
                self.n += n
            except Exception:
                # If Rich fails during update, fallback to simple
                pass

    def display(self) -> None:
        # Rich handles display automatically
        pass

    def close(self) -> None:
        if hasattr(self, '_progress') and self._progress and not self.closed:
            try:
                self._progress.stop()
            except Exception:
                pass
            self.closed = True

    def refresh(self) -> None:
        """Refresh the Rich progress bar"""
        if hasattr(self, '_progress') and self._progress and hasattr(self, '_task') and self._task is not None and not self.closed:
            try:
                # Update the task with current progress
                self._progress.update(self._task, completed=self.n)
                # Refresh the display
                self._progress.refresh()
            except Exception:
                # Fall back to base implementation if Rich fails
                super().refresh()


class SimpleProgressBar(ProgressBarBase):
    """Simple text progress bar implementation"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bar_length = 30

    def display(self) -> None:
        if self.closed:
            return

        if self.total > 0:
            percent = (self.n / self.total) * 100
            filled_length = int(self.bar_length * self.n // self.total)
            bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
            print(f"\r{self.desc}: |{bar}| {percent:.1f}% ({self.n}/{self.total} {self.unit})", end='', flush=True)
        else:
            print(f"\r{self.desc}: {self.n} {self.unit}", end='', flush=True)

    def close(self) -> None:
        if not self.closed:
            print()  # New line
            self.closed = True


class DummyProgressBar(ProgressBarBase):
    """Dummy progress bar that does nothing (when disabled)"""

    def display(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


def _has_rich_support() -> bool:
    """Check if Rich is available and terminal supports it"""
    try:
        import rich
        # Additional checks could be added here for terminal capability
        return True
    except ImportError:
        return False


def _get_progress_bar_class(mode: str = "auto"):
    """
    Get appropriate progress bar class based on mode and availability

    Args:
        mode: "auto"|"rich"|"simple"
    """
    if mode == "rich":
        return RichProgressBar
    elif mode == "simple":
        return SimpleProgressBar
    else:  # auto mode
        return RichProgressBar if _has_rich_support() else SimpleProgressBar


def progress_bar(iterable=None, total=None, desc="", unit="it",
                 disable=False, mode="auto", **kwargs):
    """
    Unified progress bar interface with automatic fallback.

    Args:
        iterable: Iterable to wrap with progress bar
        total: Total number of iterations
        desc: Description text
        unit: Unit of measurement
        disable: Disable progress bar
        mode: Progress bar mode ("auto", "rich", "simple")

    Examples:
        # Automatic mode (recommended)
        for i in progress_bar(range(100)):
            time.sleep(0.01)

        # Manual control
        with progress_bar(total=100, desc="Processing") as pbar:
            for i in range(100):
                # work
                pbar.update(1)

        # Force specific mode
        for i in progress_bar(range(100), mode="simple"):
            time.sleep(0.01)
    """
    if disable:
        return DummyProgressBar(iterable, total, desc, unit, **kwargs)

    # Get appropriate progress bar class
    pb_class = _get_progress_bar_class(mode)
    pb = pb_class(iterable, total, desc, unit, **kwargs)

    # If used as context manager or manual control
    if iterable is None and total is not None:
        return pb

    # If used as iterator
    return pb