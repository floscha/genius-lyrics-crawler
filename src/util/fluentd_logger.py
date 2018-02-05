from io import BytesIO
import logging

from fluent import handler
import msgpack


# Set general logging config.
logging.basicConfig(level=logging.INFO)


# Define additional fields for Fluentd log entries.
custom_format = {
  'where': '%(module)s.%(funcName)s',
  'type': '%(levelname)s',
  'stack_trace': '%(exc_text)s'
}


def overflow_handler(pendings):
    unpacker = msgpack.Unpacker(BytesIO(pendings))
    for unpacked in unpacker:
        print(unpacked)


def get_logger(name, fluentd_host='localhost', fluentd_port=24224):
    """Get a Python logger instance which forwards logs to Fluentd."""
    logger = logging.getLogger(name)
    fluent_handler = handler.FluentHandler(
        'mole.logs',
        host=fluentd_host,
        port=fluentd_port,
        buffer_overflow_handler=overflow_handler
    )
    formatter = fluent_handler.FluentRecordFormatter(
        custom_format,
        format_json=False
    )
    fluent_handler.setFormatter(formatter)
    logger.addHandler(fluent_handler)
    return logger
