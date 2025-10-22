import socket
import select, socket

from logging_config import logger


LENGTH_FIELD_SIZE = 4
CONNECTION_PORT = 8888
LISTEN_EVERYONE_IP = '0.0.0.0'
LISTEN_LOOPBACK_IP = '127.0.0.1'
SERVER_IP = socket.gethostbyname(socket.gethostname())  # when run on the same network interface # delete - in different constants

CALCULATE_OPERATION_CODE = '1'
EXIT_OPERATION_CODE = '2'
ERROR_OPERATION_CODE = '3'
CLIENT_OPERATION_CODES = [CALCULATE_OPERATION_CODE, EXIT_OPERATION_CODE]
SUPPORTED_EXERCISE_OPERATIONS = ['+', '-', '*', '/']
EXERCISE_SEPARATOR = ' '

WELCOME_MSG = '~~ Welcome to calculator - A place where calculating is eazy ~~'
INSTRUCTIONS = ('build your answer step by step:\n'
                '\t1. operation code: 1 - CALCULATING your question, 2 - EXIT\n'
                '\t2. first number\n'
                '\t3. space\n'
                '\t4. operation (acceptable: +, -, *, /)\n'
                '\t5. space\n'
                '\t6. second number')
LEADING_QUESTION = 'Enter your question according to the instructions above.'

NUMBERS_ERROR_MSG = 'Error with msg\\exercise numbers: Please ensure a valid operation code and numbers'
OPERATION_ERROR_MSG = 'Error with exercise operation: Please ensure a valid operation'
STRUCTURE_ERROR_MSG = 'Error with exercise structure: Please ensure you added the spaces that needed'


def garbage_cleaner(my_socket: socket.socket, timeout=0.01) -> None:
    """" Drains all available data from a socket without blocking. """

    my_socket.setblocking(False)
    try:
        while True:
            readable, _, _ = select.select([my_socket], [], [], timeout)
            if not readable:
                break
            data = my_socket.recv(4096)
            if not data:
                break
    finally:
        my_socket.setblocking(True)


def build_segment(payload: str) -> bytes:
    """ Creates and returns a valid protocol message, with length field. """
    return f"{str(len(payload.encode())).zfill(LENGTH_FIELD_SIZE)}{payload}".encode('utf-8')


def send_segment(my_socket: socket.socket, payload: str) -> None:
    """
    Send a complete segment through the given socket.

    Ensures all bytes of the segment (built from payload) are sent, retrying
    until done. Handles connection reset or unexpected errors gracefully.

    :return: None
    """

    data = build_segment(payload)
    sent_to_buffer = 0

    while sent_to_buffer != len(data):
        try:
            sent_to_buffer += my_socket.send(data[sent_to_buffer:])
        except ConnectionResetError:
            logger.warning("The other side unexpectedly closed the connection; source: send_segment")
            break
        except Exception as e:
            logger.error(f"Unexpected ERROR at send_segment: {e}")
            break


def get_payload(my_socket: socket.socket) -> tuple[bool, str]:
    """
    Extract message from protocol, without the length field.
    Handles connection reset or unexpected errors gracefully.

    :return: Tuple of boolean (True if valid, False otherwise) and string (payload if valid, error msg otherwise).
    """

    try:
        encode_payload_len: str = my_socket.recv(LENGTH_FIELD_SIZE).decode('utf-8')  # will be always LENGTH_FIELD_SIZE because protocol puts it in the beginning of each message

        if encode_payload_len == "":  # means that the other side closed the connection
            logger.warning("The other side of the socket is closed!")
            return False, ConnectionAbortedError.__name__

        payload: str = my_socket.recv(int(encode_payload_len)).decode('utf-8')

        if encode_payload_len.isdigit() and int(encode_payload_len) == len(payload.encode()):
            return True, payload

        garbage_cleaner(my_socket)
        return False, "General Error"

    except ConnectionResetError as e:
        logger.warning("The other side unexpectedly closed the connection; source: get_payload")
        return False, e.__name__
    except Exception as e:
        logger.error(f"Unexpected ERROR at get_payload: {e}")
        return False, e.__name__
