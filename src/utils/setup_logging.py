import logging
import sys
import os
import coloredlogs

# --- Custom Log Level Definition ---
# You can define custom log levels and then style them below.
# This part can be moved to a more central part of your application if needed.
NOTICE_LEVEL_NUM = 25  # A value between INFO (20) and WARNING (30)
logging.addLevelName(NOTICE_LEVEL_NUM, "NOTICE")

def notice(self, message, *args, **kws):
    if self.isEnabledFor(NOTICE_LEVEL_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(NOTICE_LEVEL_NUM, message, args, **kws)

logging.Logger.notice = notice
# ------------------------------------

def setup_colored_logging(log_file_path):
    """
    Configures the root logger to output to a file and a colored console.

    Args:
        log_file_path (str): The full path to the log file.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear any existing handlers to prevent duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- File Handler (writes to a file) ---
    # Ensure the directory for the log file exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # --- Console Handler (writes to the terminal with colors) ---
    console_handler = logging.StreamHandler(sys.stdout)
    
    # --- Custom Color and Style Definitions ---
    # Here you can define your own colors for each log level.
    # The keys are the log level names (uppercase) and values are dicts with color/style info.
    level_styles = {
        'debug': {'color': 'blue'},
        'info': {'color': 'blue'},
        'notice': {'color': 'green', 'underline': True}, # Custom level style
        'warning': {'color': 'magenta', 'italic': True},
        'error': {'color': 'red'},
        'critical': {'color': 'red', 'bold': True, 'background': 'yellow'},
    }
    
    # You can also style the fields like 'asctime', 'hostname', 'levelname', 'name', 'programname'
    field_styles = {
        'asctime': {'color': 'green'},
        'levelname': {'color': 'black', 'bold': True},
        'name': {'color': 'blue'},
    }

    console_formatter = coloredlogs.ColoredFormatter(
        fmt='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
        level_styles=level_styles,
        field_styles=field_styles
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)


class _StreamToLogger(object):
   """
   Internal file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      # Avoid logging empty lines that might come from print()
      stripped_buf = buf.rstrip()
      if stripped_buf:
          for line in stripped_buf.splitlines():
              self.logger.log(self.log_level, line.rstrip())

   def flush(self):
      pass # No need to flush for logger

def redirect_stdout_stderr_to_log(stdout_log_name='STDOUT', stderr_log_name='STDERR'):
    """
    Redirects stdout and stderr to loggers with specified names.
    Note: `setup_colored_logging` should be called first.

    Args:
        stdout_log_name (str): The name to use for the stdout logger. Defaults to 'STDOUT'.
        stderr_log_name (str): The name to use for the stderr logger. Defaults to 'STDERR'.
    """
    stdout_logger = logging.getLogger(stdout_log_name)
    sys.stdout = _StreamToLogger(stdout_logger, logging.INFO)
    
    stderr_logger = logging.getLogger(stderr_log_name)
    sys.stderr = _StreamToLogger(stderr_logger, logging.INFO) 