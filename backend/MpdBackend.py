from threading import Thread
from mpd import MPDClient
from loguru import logger as log
from queue import Empty
from multiprocessing import Queue
import functools
import inspect

def cmd(name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            if not self.is_connected():
                return

            self._cmd_queue.put(name)
        
        wrapper._cmd = name
        wrapper._func = func
        return wrapper

    return decorator


class MpdBackend:

    def __init__(self):
        self._host = ""
        self._port = 6660
        self._client: MPDClient|None = None
        self.status = {}
        self._listeners = {}
        self._cmd_queue = Queue()
        self._init_commands()

    def _init_commands(self):
        self._cmds = {}
        for _, method in inspect.getmembers(MpdBackend, predicate=inspect.isfunction):
            if not hasattr(method, "_cmd") or not hasattr(method, "_func"):
                continue

            self._cmds[method._cmd] = method._func
        log.debug(f"Found {len(self._cmds)} commands")

    def is_connected(self) -> bool:
        return self._client is not None

    @cmd("disconnect")
    def disconnect(self) -> None:
        self._client.disconnect()
        self._client = None
        self._refresh_status()

    @cmd("play-toggle")
    def play_toggle(self):
        state = self.status.get("state")
        if state == "play":
            self._client.pause()
        elif state is None:
            ...
        else:
            self._client.play()
        self._refresh_status()

    @cmd("pause")
    def pause(self):
        self._client.pause()
        self._refresh_status()

    @cmd("stop")
    def stop(self):
        self._client.stop()
        self._refresh_status()

    @cmd("next")
    def next(self):
        self._client.next()

    def set_host(self, host):
        if self._host == host:
            if not self.is_connected():
                self._connect()

            return

        self._host = host
        self._connect()

    def set_port(self, port):
        if self._port == port:
            if not self.is_connected():
                self._connect()

            return

        self._port = port
        self._connect()

    def listen(self, prop, cb):
        if prop not in self._listeners:
            self._listeners[prop] = []
        self._listeners[prop].append(cb)

    def _connect(self):
        if self._client is not None:
            self._client.close()
            self._client.disconnect()
        else:
            self._client = MPDClient()

        try:
            self._client.connect(self._host, self._port)
            log.info(f"Connected to MPD on {self._host}:{self._port}")
            self._refresh_status()
            self._start_idle()
        except BaseException as e:
            self._client = None
            log.warning(f"Connection to MPD on {self._host}:{self._port} failed", e)

    def _start_idle(self):
        Thread(target=self._idle_thread, daemon=True).start()

    def _idle_thread(self):
        while self.is_connected():
            try:
                action = self._cmd_queue.get(timeout=1)
                cb = self._cmds.get(action)
                if cb is None:
                    log.warning(f"Unexpected command: {action}")
                else:
                    cb(self)
                    continue

            except Empty:
                ...

            self._refresh_status()

    def _refresh_status(self):
        if not self.is_connected():
            self.status = {}
            return

        new_status = self._client.status()

        for k, v in self._listeners.items():
            if self.status[k] != new_status[k]:
                log.debug(f"Change in MPD state: {k} old={self.status[k]} new={new_status[k]}")
                for cb in v:
                    try:
                        cb(self.status[k], new_status[k])
                    except BaseException as e:
                        log.warning("Exception in status callback: " + e)

        self.status = new_status
        #log.debug(f"MPD Status: {self._status}")

        