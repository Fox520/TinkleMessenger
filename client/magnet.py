'''
Magnet
======

Magnet is a Container widget that allows you to automatically Animate
its chirdren to fit to the values of its properties. It makes, for
example, animating the transition of your widget to a new position, very
transparent.

BoxLayout:
    Magnet:
        transitions: {'pos': 'out_quad', 'size': 'out_elastic'}
        duration: 1
        Label:
            text: 'test'
    Magnet:
        transitions: {'x: 'out_quad', 'y': 'linear', 'size': 'out_elastic'}
        duration: 2
        Label:
            text: 'test'
    Magnet:
        transitions: {'pos': 'linear', 'width': 'out_sin', 'height': 'in_sine'}
        duration: 3
        Label:
            text: 'test'


If new elements are added to this BoxLayout, or if the size/pos of this
BoxLayout changes, the widgets will move to their new positions and
size, using the defined transitions for each property.

You can use Magnet for other properties, as you see fit, of course.
'''

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, DictProperty
from kivy.lang import Builder
from kivy.clock import Clock
from random import sample, randint, random


class Magnet(Widget):
    transitions = DictProperty({'pos': 'out_quad', 'size': 'linear'})
    duration = NumericProperty(1)
    anims = ListProperty([])

    def __init__(self, **kwargs):
        super(Magnet, self).__init__(**kwargs)
        self.bind(**{k: self.attract for k in self.transitions})

    def on_children(self, *args):
        if len(self.children) > 1:
            raise ValueError('Magnet can have only one children')
        else:
            self.attract()

    def attract(self, *args):
        if not self.children:
            return

        if self.anims:
            for a in self.anims:
                a.stop(self.children[0])
            self.anims = []

        for t in self.transitions:
            a = Animation(t=self.transitions[t], d=self.duration,
                          **{t: getattr(self, t), })

            a.start(self.children[0])
            self.anims.append(a)


# after that it's for the demo
kvdemo = '''
GridLayout:
    cols: 3
'''

transitions = (
    'out_sine', 'out_quint', 'out_quart', 'out_quad', 'out_expo',
    'out_cubic', 'out_circ', 'out_bounce', 'out_back', 'linear',
    'in_sine', 'in_quint', 'in_quart', 'in_quad', 'in_out_sine',
    'in_out_quint', 'in_out_quart', 'in_out_quad', 'in_out_expo',
    'in_out_cubic', 'in_out_circ', 'in_out_bounce', 'in_out_back',
    'in_expo', 'in_cubic', 'in_circ', 'in_bounce', 'in_back',
    )


class MagnetDemo(App):
    def build(self):
        self.root = Builder.load_string(kvdemo)
        Clock.schedule_interval(self.add_child, 1)
        Clock.schedule_interval(self.add_col, 5)
        Clock.schedule_interval(self.scramble, 10)
        return self.root

    def add_child(self, dt, *args):
        magnet = Magnet(transitions={'pos': sample(transitions, 1)[0],
                                     'size': sample(transitions, 1)[0]},
                        duration=random())
        magnet.add_widget(Button(text='test %s' % dt))
        self.root.add_widget(magnet, index=randint(0, len(self.root.children)))

    def add_col(self, *args):
        self.root.cols += 1

    def scramble(self, *args):
        for i in sample(self.root.children, len(self.root.children)):
            self.root.remove_widget(i)
            self.root.add_widget(i)

if __name__ == '__main__':
    MagnetDemo().run()
