import os
import hmac
import hashlib
import logging
import tornado
import functools
from tornado.log import access_log

from webserver.utils import get_bool_env

from pathlib import Path

INSTALL_ROOT = Path.cwd().absolute()

_LOGGER = logging.getLogger(__name__)

ENV_DEV = "WEBSERVER_DEV"

def password_hash(password: str) -> bytes:
    """Create a hash of a password to transform it to a fixed-length digest.

    Note this is not meant for secure storage, but for securely comparing passwords.
    """
    return hashlib.sha256(password.encode()).digest()

class ServerSettings:
    def __init__(self):
        self.config_dir = ""
        self.password_hash = ""
        self.username = ""
        self.using_password = False
        self.on_ha_addon = False
        self.cookie_secret = None

    def parse_args(self, args):
        self.on_ha_addon = args.ha_addon
        password = args.password or os.getenv("PASSWORD", "")
        if not self.on_ha_addon:
            self.username = args.username or os.getenv("USERNAME", "")
            self.using_password = bool(password)
        if self.using_password:
            self.password_hash = password_hash(password)
        # self.config_dir = args.configuration

    @property
    def relative_url(self):
        return os.getenv("WEBSERVER_RELATIVE_URL", "/")

    @property
    def using_auth(self):
        return self.using_password or self.using_ha_addon_auth

    def check_password(self, username, password):
        if not self.using_auth:
            return True
        if username != self.username:
            return False

        # Compare password in constant running time (to prevent timing attacks)
        return hmac.compare_digest(self.password_hash, password_hash(password))

    def rel_path(self, *args):
        return os.path.join(self.config_dir, *args)


settings = ServerSettings()

cookie_authenticated_yes = b"yes"

def get_base_frontend_path():
    # if ENV_DEV not in os.environ:
    #     # TODO: Package Frontend if needed
    #     import webserver

    #     return webserver.where()

    if ENV_DEV not in os.environ:
        static_path = INSTALL_ROOT.joinpath("webserver/templates/").resolve().as_posix()
    else:
        static_path = os.environ[ENV_DEV]

    if not static_path.endswith("/"):
        static_path += "/"

    # This path can be relative, so resolve against the root or else templates don't work
    return os.path.abspath(os.path.join(os.getcwd(), static_path, ""))

def get_static_path(*args):
    return os.path.join(get_base_frontend_path(), "static", *args)

@functools.cache
def get_static_file_url(name):
    base = f"./static/{name}"

    if ENV_DEV in os.environ:
        return base

    path = get_static_path(name)
    with open(path, "rb") as f_handle:
        hash_ = hashlib.md5(f_handle.read()).hexdigest()[:8]
    return f"{base}?hash={hash_}"

def template_args():
    return {
        "get_static_file_url": get_static_file_url,
        "relative_url": settings.relative_url,
    }

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # self.write("Hello, world")
        self.render("omnifood.template.html", **template_args())

class LocaleHandler(tornado.web.RequestHandler):
    def get(self, locale):
        self.locale = tornado.locale.get(locale)
        self.render("index.html", product=1, author='Wai Foong', view=1234)

def make_app(debug=get_bool_env(ENV_DEV)):
    def log_function(handler):
        if handler.get_status() < 400:
            log_method = access_log.info

        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error

        request_time = 1000.0 * handler.request.request_time()
        # pylint: disable=protected-access
        log_method(
            "%d %s %.2fms",
            handler.get_status(),
            handler._request_summary(),
            request_time,
        )

    class StaticFileHandler(tornado.web.StaticFileHandler):
        def set_extra_headers(self, path):
            if "favicon.ico" in path:
                self.set_header("Cache-Control", "max-age=84600, public")
            else:
                self.set_header(
                    "Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"
                )

    app_settings = {
        "debug": debug,
        "cookie_secret": settings.cookie_secret,
        "log_function": log_function,
        "websocket_ping_interval": 30.0,
        "template_path": get_base_frontend_path(),
    }
    tornado.locale.load_translations(f"{app_settings['template_path']}/locale/"
)
    rel = settings.relative_url
    app = tornado.web.Application(
        [
            (f"{rel}", MainHandler),
            (f"{rel}([^/]+)/about-us", LocaleHandler),
            (f"{rel}static/(.*)", StaticFileHandler, {"path": get_static_path()}),
        ],
        **app_settings,
    )

    return app

def start_web_server(args):
    settings.parse_args(args)

    app = make_app(args.verbose)

    if args.socket is not None:
        _LOGGER.info(
            "Starting web server on unix socket %s and configuration dir %s...",
            args.socket,
            settings.config_dir,
        )
        server = tornado.httpserver.HTTPServer(app)
        socket = tornado.netutil.bind_unix_socket(args.socket, mode=0o666)
        server.add_socket(socket)
    else:
        _LOGGER.info(
            "Starting web server on http://%s:%s and configuration dir %s...",
            args.address,
            args.port,
            settings.config_dir,
        )
        app.listen(args.port, args.address)

        if args.open_ui:
            import webbrowser

            webbrowser.open(f"http://{args.address}:{args.port}")

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        if args.socket is not None:
            os.remove(args.socket)