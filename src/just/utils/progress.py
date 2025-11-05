"""Unified progress bar interface with automatic fallback between Rich and simple text implementations."""
import os
import sys
import time

from abc import ABC, abstractmethod
from typing import Iterator, Any

from rich.progress import Progress, BarColumn, TextColumn
from rich.progress import SpinnerColumn


class ProgressBarBase(ABC):
    """Base class for progress bars"""

    def __init__(self, iterable=None, *, total=None, desc="", unit="it", **kwargs):
        self.iterable = iterable
        # If iterable is None, total must be provided
        if iterable is None and total is None:
            raise ValueError("total must be provided when iterable is None")

        # total must be greater than or equal to 0
        if total is not None and total <= 0:
            raise ValueError("total must be greater than or equal to 0")

        if iterable and total is not None and total != len(iterable):
            raise ValueError("total must be equal to the length of iterable")

        # Set total, handling the case where total is 0 or None
        if total is not None:
            self.total = total
        elif iterable is not None:
            self.total = len(iterable)
        else:
            self.total = 0

        self.desc = desc
        self.unit = unit
        self.n = 0
        self.closed = False
        self._started = False  # Track if progress bar has been started
        self.start_time = None  # Initialize start_time

    def __iter__(self) -> Iterator[Any]:
        if self.iterable is None:
            raise TypeError("Must provide iterable to iterate over")

        # Start the progress bar if it hasn't been started yet
        if not self._started:
            self.start()
            self._started = True

        try:
            for obj in self.iterable:
                yield obj
                self.update(1)
        finally:
            # Close the progress bar when iteration is complete
            if not self.closed:
                self.close()

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
        self.start_time = time.time()

    def close(self) -> None:
        """Close the progress bar"""
        self.closed = True

    def refresh(self) -> None:
        """Refresh the progress bar display (safe implementation)"""
        self.display()


    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time with intelligent units"""
        if seconds < 0:
            seconds = 0

        # For very short times (less than 1 minute), show in seconds with 1 decimal place
        if seconds < 60:
            return f"{seconds:.1f}s"

        # For times up to 1 hour, show in minutes and seconds
        if seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if secs > 0:
                return f"{minutes}m{secs}s"
            else:
                return f"{minutes}m"

        # For times up to 1 day, show in hours, minutes and seconds
        if seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if minutes > 0 and secs > 0:
                return f"{hours}h{minutes}m{secs}s"
            elif minutes > 0:
                return f"{hours}h{minutes}m"
            elif secs > 0:
                return f"{hours}h{secs}s"
            else:
                return f"{hours}h"

        # For longer times, show in days, hours, minutes and seconds
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0 and minutes > 0 and secs > 0:
            return f"{days}d{hours}h{minutes}m{secs}s"
        elif hours > 0 and minutes > 0:
            return f"{days}d{hours}h{minutes}m"
        elif hours > 0 and secs > 0:
            return f"{days}d{hours}h{secs}s"
        elif hours > 0:
            return f"{days}d{hours}h"
        elif minutes > 0 and secs > 0:
            return f"{days}d{minutes}m{secs}s"
        elif minutes > 0:
            return f"{days}d{minutes}m"
        elif secs > 0:
            return f"{days}d{secs}s"
        else:
            return f"{days}d"


    @abstractmethod
    def display(self) -> None:
        """Display current progress"""
        pass


class RichProgressBar(ProgressBarBase):
    """Rich progress bar implementation with enhanced visuals"""

    def __init__(self, iterable=None, *, total=None, desc="", unit="it",
                 progress_desc_columns=None, progress_desc_formatter=None, **kwargs):
        super().__init__(iterable, total=total, desc=desc, unit=unit, **kwargs)
        self.progress_desc_formatter = progress_desc_formatter

        # Create base columns for the progress bar (<logo><desc><progress_bar><percent>)
        base_columns = [
            SpinnerColumn(),
            TextColumn("[bold #fde047]{task.description}"),  # Bright warm yellow
            BarColumn(
                bar_width=40,
                complete_style="#4ade80",  # Soft green
                finished_style="#4ade80",  # Keep green when finished
                pulse_style="#f472b6",  # Pinker red
                style="#9ca3af"  # Medium gray background
            ),
            TextColumn("[bold #f472b6]{task.percentage:>3.0f}%"),  # Pinker red
        ]

        # Separator between percent and progress_desc
        percent_separator = [TextColumn("•")]

        # Determine description area columns (<progress_desc>)
        if progress_desc_columns is not None:
            # Use custom columns for description area
            desc_columns = progress_desc_columns
        elif progress_desc_formatter is not None:
            # Use formatter function with TextColumn
            desc_columns = [
                TextColumn("{task.fields[desc_text]}")
            ]
        else:
            # Default behavior: use original description columns
            desc_columns = [
                TextColumn(
                    "[bold #06b6d4]{task.completed}/{task.total}[/bold #06b6d4] "
                    "[#eab308]{task.fields[unit]}[/#eab308]"
                ),  # Teal numbers, amber unit
            ]

        # Time columns are always present (<time_cost>)
        time_columns = [
            TextColumn("•"),
            TextColumn(
                "[[#4ade80]{task.fields[elapsed_formatted]}[/#4ade80]"
                "<[#c084fc]{task.fields[remaining_formatted]}[/#c084fc]]"
            ),  # Green/purple time
        ]

        # Combine all columns: <logo><desc><progress_bar><percent><sep><progress_desc><sep><time_cost>
        columns = base_columns + percent_separator + desc_columns + time_columns

        self._progress = Progress(*columns)
        self._task = self._progress.add_task(
            self.desc,
            total=self.total,
            unit=self.unit,
            elapsed_formatted="0.0s",
            remaining_formatted="0.0s",
            desc_text=""  # For custom formatter
        )

    def start(self) -> None:
        self._progress.start()
        # Initialize start_time for consistency with base class
        if not hasattr(self, 'start_time') or self.start_time is None:
            self.start_time = time.time()

    def update(self, n: int = 1) -> None:
        # Update the progress
        self._progress.update(self._task, advance=n)
        self.n += n

        # Calculate and format elapsed and remaining time
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if self.n > 0 and elapsed_time > 0 and self.total > 0:
            rate = self.n / elapsed_time
            remaining_items = self.total - self.n
            eta = remaining_items / rate if rate > 0 else 0
        else:
            rate = 0
            eta = 0

        # Format times using our custom formatter
        elapsed_formatted = self._format_time(elapsed_time)
        remaining_formatted = self._format_time(eta)

        # Prepare update fields
        update_fields = {
            'elapsed_formatted': elapsed_formatted,
            'remaining_formatted': remaining_formatted
        }

        # If we have a custom formatter, use it
        if self.progress_desc_formatter is not None:
            percentage = (self.n / self.total) * 100 if self.total > 0 else 0
            desc_text = self.progress_desc_formatter(
                self.n,
                self.total,
                elapsed_time,
                self.unit,
                rate,
                eta,
                percentage
            )
            update_fields['desc_text'] = desc_text

        # Update task with all fields
        self._progress.update(self._task, **update_fields)

    def display(self) -> None:
        # In iterator mode, we need to manually refresh the display
        # Rich normally handles this automatically, but in some cases we need to force it

        self._progress.refresh()


    def close(self) -> None:
        if not self.closed:
            self._progress.stop()
            self.closed = True

    def refresh(self) -> None:
        """Refresh the Rich progress bar"""
        # Update the task with current progress
        self._progress.update(self._task, completed=self.n)
        # Refresh the display
        self._progress.refresh()



class SimpleProgressBar(ProgressBarBase):
    """Simple text progress bar implementation"""

    def __init__(self, iterable=None, *, total=None, desc="", unit="it",
                 progress_desc_formatter=None, **kwargs):
        super().__init__(iterable, total=total, desc=desc, unit=unit, **kwargs)
        self.bar_length = 30
        self.start_time = None
        self.progress_desc_formatter = progress_desc_formatter

    def display(self) -> None:
        if self.closed:
            return

        if self.total > 0:
            # Calculate elapsed time
            elapsed_time = time.time() - self.start_time if self.start_time else 0

            # Calculate estimated remaining time and rate
            if self.n > 0 and elapsed_time > 0:
                rate = self.n / elapsed_time
                remaining_items = self.total - self.n
                eta = remaining_items / rate if rate > 0 else 0
            else:
                rate = 0
                eta = 0

            # Format time values
            elapsed_str = self._format_time(elapsed_time)
            eta_str = self._format_time(eta)

            percent = (self.n / self.total) * 100
            filled_length = int(self.bar_length * self.n // self.total)
            bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
            # Always show percentage with 1 decimal place for consistency
            percent_display = f"{percent:.1f}"

            # Use custom formatter if provided, otherwise use default
            if self.progress_desc_formatter is not None:
                percentage = percent
                progress_desc = self.progress_desc_formatter(
                    self.n,
                    self.total,
                    elapsed_time,
                    self.unit,
                    rate,
                    eta,
                    percentage
                )
            else:
                progress_desc = f"({self.n}/{self.total} {self.unit})"

            progress_text = (
                f"\r{self.desc}: |{bar}| {percent_display}% "
                f"• {progress_desc} "
                f"• [{elapsed_str}<{eta_str}]"
            )
            # Ensure consistent width to prevent text jumping
            # Calculate a reasonable maximum width for the progress text
            # Using example values for maximum length fields
            example_desc = " " * 30  # Reserve space for description
            example_elapsed = "999.9s"  # Example of longest time format
            example_eta = "999.9s"      # Example of longest time format
            max_width = len(f"{self.desc}: |{'█' * self.bar_length}| 100.0% {example_desc} [{example_elapsed}<{example_eta}]")
            progress_text = progress_text.ljust(max_width)
            print(progress_text, end='', flush=True)
        else:
            # For unknown total, just show elapsed time
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            elapsed_str = self._format_time(elapsed_time)
            progress_text = f"\r{self.desc}: {self.n} {self.unit} [{elapsed_str}]"
            print(progress_text, end='', flush=True)

    def close(self) -> None:
        if not self.closed:
            print()  # New line
            self.closed = True




def _terminal_supports_rich() -> bool:
    """Check if terminal supports Rich advanced display features"""
    # Check if we're in a terminal that supports Rich
    if not sys.stdout.isatty():
        return False

    term = os.getenv('TERM', '')
    if term in ('dumb', 'unknown'):
        return False

    # Additional checks could be added here for specific terminal capabilities
    return True


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
        # In auto mode, use Rich if terminal supports it
        return RichProgressBar if _terminal_supports_rich() else SimpleProgressBar


def progress_bar(
    iterable=None,
    desc="",
    unit="it",
    *,
    total=None,
    mode="auto",
    progress_desc_columns=None,
    progress_desc_formatter=None,
    **kwargs
):
    """
    Unified progress bar interface with automatic fallback.

    Args:
        iterable: Iterable to wrap with progress bar
        total: Total number of iterations (keyword-only argument)
        desc: Description text
        unit: Unit of measurement
        mode: Progress bar mode ("auto", "rich", "simple")
        progress_desc_columns: List of Rich columns to use for the description area (Rich mode only)
        progress_desc_formatter: Function to format progress description (compatible with both modes)

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

        # Custom columns for Rich mode
        from rich.progress import FileSizeColumn, TransferSpeedColumn
        columns = [FileSizeColumn(), TransferSpeedColumn()]
        for i in progress_bar(range(100), progress_desc_columns=columns):
            time.sleep(0.01)

        # Custom formatter for both modes
        def download_formatter(completed, total, elapsed, unit, speed=None, **kwargs):
            return f"{completed}/{total} {unit} @ {speed:.1f}{unit}/s"
        for i in progress_bar(range(100), progress_desc_formatter=download_formatter):
            time.sleep(0.01)
    """
    # Get appropriate progress bar class
    pb_class = _get_progress_bar_class(mode)
    pb = pb_class(iterable, total=total, desc=desc, unit=unit,
                  progress_desc_columns=progress_desc_columns,
                  progress_desc_formatter=progress_desc_formatter, **kwargs)

    # If used as context manager or manual control
    if iterable is None and total is not None:
        return pb

    # If used as iterator
    return pb