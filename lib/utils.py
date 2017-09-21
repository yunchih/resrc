import logging, sys

def quit(*args):
    if len(args):
        logging.error(str(args[0]) % args[1:])
    sys.exit(1)

def open_file(fn, mode="r"):
    try:
        return open(prompt, mode)
    except FileNotFoundError:
        print("File {0} does not exist.".format(fn))
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
