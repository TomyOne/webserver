import sys
import logging
import argparse

from webserver.log import setup_log

_LOGGER = logging.getLogger(__name__)

class WebServerError(Exception):
    """General WebServer exception occurred."""

def command_webserver(args):
    from webserver.server import server

    return server.start_web_server(args)


PRE_CONFIG_ACTIONS = {
    "webserver": command_webserver,
}

def parse_args(argv):
    options_parser = argparse.ArgumentParser(add_help=False)
    options_parser.add_argument(
        "-v", "--verbose", help="Enable verbose logs.", action="store_true"
    )
    options_parser.add_argument(
        "-q", "--quiet", help="Disable all logs.", action="store_true"
    )

    parser = argparse.ArgumentParser(
        description=f"WebServer v0.0.1", parents=[options_parser] # {const.__version__}
    )

    subparsers = parser.add_subparsers(
        help="Command to run:", dest="command", metavar="command"
    )

    subparsers.required = True

    subparsers.add_parser("version", help="Print the WebServer version and exit.")

    parser_server = subparsers.add_parser(
        "webserver", help="Create a WebServer."
    )

    parser_server.add_argument(
        "--port",
        help="The HTTP port to open connections on. Defaults to 8888.",
        type=int,
        default=8888,
    )
    parser_server.add_argument(
        "--address",
        help="The address to bind to.",
        type=str,
        default="0.0.0.0",
    )
    parser_server.add_argument(
        "--username",
        help="The optional username to require for authentication.",
        type=str,
        default="",
    )
    parser_server.add_argument(
        "--password",
        help="The optional password to require for authentication.",
        type=str,
        default="",
    )
    parser_server.add_argument(
        "--open-ui", help="Open the WebServer in a browser.", action="store_true"
    )
    parser_server.add_argument(
        "--ha-addon", help=argparse.SUPPRESS, action="store_true"
    )
    parser_server.add_argument(
        "--socket", help="Make the WebServer serve under a unix socket", type=str
    )

    arguments = argv[1:]

    def _raise(x):
        raise argparse.ArgumentError(None, x)

    # current_parser = argparse.ArgumentParser(add_help=False, parents=[parser])
    # current_parser.set_defaults(deprecated_argv_suggestion=None)
    # current_parser.error = _raise
    # return current_parser.parse_args(arguments)
    try:
        # duplicate parser so that we can use the original one to raise errors later on
        current_parser = argparse.ArgumentParser(add_help=False, parents=[parser])
        current_parser.set_defaults(deprecated_argv_suggestion=None)
        current_parser.error = _raise
        return current_parser.parse_args(arguments)
    except argparse.ArgumentError:
        pass

    compat_parser = argparse.ArgumentParser(parents=[options_parser], add_help=False)
    compat_parser.add_argument("-h", "--help", action="store_true")
    compat_parser.add_argument("configuration", nargs="*")
    compat_parser.add_argument(
        "command",
        choices=[
            "webserver",
        ],
    )

    try:
        compat_parser.error = _raise
        result, unparsed = compat_parser.parse_known_args(argv[1:])
        last_option = len(arguments) - len(unparsed) - 1 - len(result.configuration)
        unparsed = [
            "--device" if arg in ("--upload-port", "--serial-port") else arg
            for arg in unparsed
        ]
        arguments = (
            arguments[0:last_option]
            + [result.command]
            + result.configuration
            + unparsed
        )
        deprecated_argv_suggestion = arguments
    except argparse.ArgumentError:
        # old-style parsing failed, don't suggest any argument
        deprecated_argv_suggestion = None

    # Finally, run the new-style parser again with the possibly swapped arguments,
    # and let it error out if the command is unparsable.
    parser.set_defaults(deprecated_argv_suggestion=deprecated_argv_suggestion)
    return parser.parse_args(arguments)


def run_server(argv):
    args = parse_args(argv)

    setup_log(
        args.verbose,
        args.quiet,
        # Show timestamp for webserver access logs
        args.command == "webserver",
    )

    if sys.version_info < (3, 8, 0):
        _LOGGER.error(
            "You're running WebServer with Python <3.8. Please reinstall with Python 3.8+"
        )
        return 1

    if args.command in PRE_CONFIG_ACTIONS:
        try:
            return PRE_CONFIG_ACTIONS[args.command](args)
        except WebServerError as e:
            _LOGGER.error(e, exc_info=args.verbose)
            return 1

def main():
    try:
        return run_server(sys.argv)
    except WebServerError as e:
        _LOGGER.error(e)
        return 1
    except KeyboardInterrupt:
        return 1

if __name__ == "__main__":
    sys.exit(main())
