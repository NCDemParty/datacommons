import logging
import logging.handlers
import os.path

from django.conf import settings

class EncodingFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None, encoding=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding = encoding

    def format(self, record):
        result = logging.Formatter.format(self, record)
        if isinstance(result, unicode):
            result = result.encode(self.encoding or 'utf-8')
        return result

def set_up_logger(importer_name, log_path, email_subject, email_recipients=settings.LOGGING_EMAIL['recipients']):
    # create logger
    log = logging.getLogger(importer_name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # create console handler and set level to debug
    ch = logging.FileHandler(os.path.join(log_path, importer_name + '.log'))
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # create email handler and set level to warn
    if settings.LOGGING_EMAIL:
        eh = logging.handlers.SMTPHandler(
            (settings.LOGGING_EMAIL['host'], settings.LOGGING_EMAIL['port']), # host
            settings.LOGGING_EMAIL['username'], # from address
            email_recipients,
            '['+settings.ENVIRONMENT+'] '+email_subject,
            (settings.LOGGING_EMAIL['username'], settings.LOGGING_EMAIL['password']) # credentials tuple
        )
        eh.setLevel(logging.WARN)
        eh.setFormatter(formatter)
        eh.setFormatter(EncodingFormatter('%(message)s', encoding='iso8859-1'))
        log.addHandler(eh)

    return log
