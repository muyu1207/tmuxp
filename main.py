import kaptan
from sh import tmux, cut
from pprint import pprint
config = kaptan.Kaptan(handler="yaml")

config.import_config("""
    windows:
        - editor:
            layout: main-vertical
            panes:
                - vim
                - guard
        - server: bundle exec rails s
        - logs: tail -f logs/development.log
    """)

print config
pprint(config.__dict__)

windows = list()
# expand inline window configuration
""" expand
    dict({'session_name': { dict })

    to

    dict({ name='session_name', **dict})
"""

for window in config.get('windows'):

    if len(window) == 1:
        name = window.iterkeys().next()  # get window name

        """expand
            window[name] = 'command'

            to

            window[name] = {
                panes=['command']
            }
        """
        if isinstance(window[name], basestring):
            windowoptions = dict(
                panes=[window[name]]
            )
        else:
            windowoptions = window[name]

        window = dict(name=name, **windowoptions)
        if len(window['panes']) > 1:
            pprint('omg multiple panes')

    windows.append(window)


class Session(object):
    __FORMATS__ = [
        'session_attached', 'session_created', 'session_created_string',
        'session_group', 'session_grouped', 'session_height', 'session_id',
        'session_name', 'session_width', 'session_windows']

    def __init__(self, session_name):
        self._session_name = session_name

    @property
    def session_name(self):
        return self._session_name

    @property
    def windows(self):

        if hasattr(self, '_session_name'):
            formats = [
                'session_name', 'window_index', 'pane_index', 'window_width',
                'window_height'
            ]
            tmux_formats = ['#{%s}\t' % format for format in formats]

            windows = cut(tmux('list-windows', '-t%s' % self.session_name, \
                            '-F%s' % ''.join(tmux_formats)), '-f1', '-d:')

            windows = dict(zip(formats, windows.split('\t')))
            windows = [Window(session=self, **windows)]
            return windows
        else:
            return None  # session is not bound to a current session, the user
                         # is using Session imported config file to launch a
                         # new session

    def __repr__(self):
        # todo test without session_name
        return "%s(%s)" % (self.__class__, self.session_name)

    pass


class Window(object):
    def __init__(self, **kwargs):
        if 'session' in kwargs:
            if isinstance(kwargs['session'], Session):
                self._session = kwargs['session']

    @property
    def session(self):
        return self._session if self._session else None

    @property
    def panes(self):

        if hasattr(self.session, '_session_name'):
            formats = [
                'session_name', 'window_index', 'pane_index', 'window_width',
                'window_height', 'pane_width', 'pane_height', 'pane_pid',
                'pane_current_path'
            ]
            tmux_formats = ['#{%s}\t' % format for format in formats]

            panes = cut(tmux('list-panes',
                               '-s', # for sessions
                               '-t%s' % self.session.session_name,  # target session_name
                            '-F%s' % ''.join(tmux_formats)), '-f1', '-d:')

            panes = str(panes).split('\n')

            return [dict(zip(formats, pane.split('\t'))) for pane in panes]
        else:
            return None  # session is not bound to a current session, the user
                         # is using Session imported config file to launch a
                         # new session

    pass


class Pane(object):
    pass


pprint(tmux('list-windows'))
pprint(windows)

def list_sessions():
    for session in cut(tmux('list-sessions'), '-f1', '-d:'):
        yield Session(session.strip('\n'))

sessions = list(list_sessions())

for session in sessions:
    pprint(session)
    for window in session.windows:
        pprint(window.panes)
