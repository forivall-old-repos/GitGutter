import sublime
import sublime_plugin
try:
    from GitGutter.view_collection import ViewCollection
except ImportError:
    from view_collection import ViewCollection

ST2 = int(sublime.version()) < 3014
import time

class GitGutterEvents(sublime_plugin.EventListener):
    def __init__(self):
        self.load_settings()
        self.last_time = 0
        self.in_timeout = False

    def _view_collection_add_debounced(self, view):
        now = time.time()
        if now - self.last_time >= 1:
            self.in_timeout = False
            self.last_time = now
            ViewCollection.add(view)
        elif not self.in_timeout:
            self.in_timeout = True
            sublime.set_timeout(
                lambda:self._view_collection_add_debounced(view), 3000)

    # Synchronous

    def on_modified(self, view):
        if not self.live_mode:
            return None
        if not self.non_blocking:
            ViewCollection.add(view)
        elif ST2:
            self._view_collection_add_debounced(view)

    def on_clone(self, view):
        if not self.non_blocking:
            ViewCollection.add(view)
        elif ST2:
            now = time.time()
            if now - self.last_time >= 1:
                self.last_time = now
                sublime.set_timeout(lambda: ViewCollection.add(view), 5)

    def on_post_save(self, view):
        if not self.non_blocking:
            ViewCollection.add(view)
        elif ST2:
            now = time.time()
            if now - self.last_time >= 5:
                self.last_time = now
                sublime.set_timeout(lambda: ViewCollection.add(view), 5)

    def on_load(self, view):
        if (not self.non_blocking or ST2) and not self.live_mode:
            ViewCollection.add(view)

    def on_activated(self, view):
        if (not self.non_blocking or ST2) and self.focus_change_mode:
            ViewCollection.add(view)

    
    # Asynchronous

    def on_modified_async(self, view):
        if not self.live_mode:
            return None
        if self.non_blocking:
            ViewCollection.add(view)

    def on_clone_async(self, view):
        if self.non_blocking:
            ViewCollection.add(view)

    def on_post_save_async(self, view):
        if self.non_blocking:
            ViewCollection.add(view)

    def on_load_async(self, view):
        if self.non_blocking and not self.live_mode:
            ViewCollection.add(view)

    def on_activated_async(self, view):
        if self.non_blocking and self.focus_change_mode:
            ViewCollection.add(view)

    # Settings

    def load_settings(self):
        self.settings = sublime.load_settings('GitGutter.sublime-settings')
        
        self.live_mode = self.settings.get('live_mode')
        if self.live_mode is None: 
            self.live_mode = True

        self.focus_change_mode = self.settings.get('focus_change_mode')
        if self.focus_change_mode is None:
            self.focus_change_mode = True

        self.non_blocking = self.settings.get('non_blocking')
        if self.non_blocking is None:  # or int(sublime.version()) < 3014: 
            self.non_blocking = False
