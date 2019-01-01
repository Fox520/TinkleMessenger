from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty

TOAST_KV='''
<_Toast@Label>:
    size_hint: (None, None)
    halign: 'center'
    valign: 'middle'
    color: (1.0, 1.0, 1.0, self._transparency)
    canvas:
        Color:
            rgba: (0.5, 0.5, 0.5, self._transparency)
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: (0.0, 0.0, 0.0, 1.0)
        Rectangle:
            size: (self.size[0] - 2, self.size[1] - 2)
            pos: (self.pos[0] + 1, self.pos[1] + 1)
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)
'''

Builder.load_string(TOAST_KV)

class _Toast(Label):
    _transparency = NumericProperty(1.0)

    def __init__(self, text, *args, **kwargs):
        '''Show the toast in the main window.  The attatch_to logic from 
        :class:`~kivy.uix.modalview` isn't necessary because a toast really
        does need to go on top of everything.
        '''
        self._bound = False
        super(_Toast, self).__init__(text=text, *args, **kwargs)
    
    def show(self, length_long, *largs):
        duration = 5000 if length_long else 4000
        rampdown = duration * 0.1
        if rampdown > 500:
            rampdown = 500
        if rampdown < 100:
            rampdown = 100
        self._rampdown = rampdown
        self._duration = duration - rampdown
        Window.add_widget(self)
        Clock.schedule_interval(self._in_out, 1/60.0)

    def on_texture_size(self, instance, size):
        self.size = map(lambda i: i * 1.3, size)
        if not self._bound:
            Window.bind(on_resize=self._align)
            self._bound = True
        self._align(None, Window.size)
            
    def _align(self, win, size):
        self.x = (size[0] - self.width) / 2.0
        self.y = size[1] * 0.1

    def _in_out(self, dt):
       # print dt
        self._duration -= dt * 1000
        if self._duration <= 0:
            self._transparency = 1.0 + (self._duration / self._rampdown)
            #print self._transparency
        if -(self._duration) > self._rampdown:
            Window.remove_widget(self)
            return False

def toast(text, length_long=False):
    _Toast(text=text).show(length_long)