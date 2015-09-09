import statsd
import tornado.ioloop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient


class AsynchronousHandler(RequestHandler):

    def prepare(self):
        if self.request.method == 'GET':
            self.get_timer = statsd.timer.Timer(
                'tornado.{0}.get'.format(self.request.uri[1:]),
                self.application.statsd_conn)
            self.get_timer.start()
        self.success = False

    def on_finish(self):
        if hasattr(self, 'get_timer'):
            if self.success:
                self.get_timer.stop("success")
            else:
                self.get_timer.stop("failure")

    @asynchronous
    def get(self):
        http = AsyncHTTPClient()
        http.fetch("http://friendfeed.com/", self._on_download)

    def _on_download(self, response):
        if response.code == 200:
            self.success = True
        self.write("Downloaded!")
        self.finish()


class CoroutineHandler(RequestHandler):

    def prepare(self):
        if self.request.method == 'GET':
            self.get_timer = statsd.timer.Timer(
                'tornado.{0}.get'.format(self.request.uri[1:]),
                self.application.statsd_conn)
            self.get_timer.start()
        self.success = False

    def on_finish(self):
        if hasattr(self, 'get_timer'):
            if self.success:
                self.get_timer.stop("success")
            else:
                self.get_timer.stop("failure")

    @coroutine
    def get(self):
        http = AsyncHTTPClient()
        yield http.fetch("http://friendfeed.com/", self._on_download)
        self.write("\nDownloaded!")

    def _on_download(self, response):
        if response.code == 200:
            self.success = True
        self.write("Downloading.....")


application = Application([
    (r"/asynchronous", AsynchronousHandler),
    (r"/coroutine", CoroutineHandler),
])

STATSD_ENABLED = False
STATSD_HOST = 'localhost'
STATSD_PORT = 8125

application.statsd_conn = statsd.connection.Connection(
    host=STATSD_HOST,
    port=STATSD_PORT,
    sample_rate=1,
    disabled=False)

if __name__ == "__main__":
    application.listen(address='localhost', port=8888)
    tornado.ioloop.IOLoop.current().start()
