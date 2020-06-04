import atexit

import attr
import fbchat
import rx
import rx.operators

from .listeners import EventListeners
from .util import get_session, save_session


@attr.s
class Patrick:
    config = attr.ib()

    _listeners: EventListeners = attr.ib(EventListeners())

    def listen(self):
        session, status = get_session(self.config)
        atexit.register(lambda: save_session(session))
        print(f"{status}, user {session.user.id}")

        # TODO Figure out what these kwargs do
        chat_listener = fbchat.Listener(session=session, chat_on=True, foreground=True)

        # Listener event loop
        print("Listening...")
        for event in chat_listener.listen():
            self._listeners.handle(event)

        # source = rx.operators.publish(rx.from_(listener.listen()))

        # source.subscribe(lambda value: print("Received {0}".format(value)),)
        # source.subscribe(lambda value: print("Received again {0}".format(value)))

        # source.connect()

        # for event in listener.listen():
        #    print(event)

        # Don't send any thread events down the event bus if the thread is not in the allow list
        # if isinstance(event, fbchat.ThreadEvent) and ignore_thread(event.thread.id):
        #     continue
        # event_bus.send(type(event), event=event)
