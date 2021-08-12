"""
Die Anzeige für ein Scenario.
"""
from typing import Sequence
__author__ = "jasper"
from gi.repository import Gtk, cairo

class PixelArtDrawingArea(Gtk.DrawingArea):
    """Ein einziges Bild eines Scenarios (die Kacheln)"""
    BG = (0.125, 0.125, 0.125)
    FG = (0.9, 0.9, 0.9)
    def __init__(self, header: str, feld: Sequence[Sequence[object]]):
        super().__init__(visible=True, vexpand=True, hexpand=True)
        self.header = header
        self.feld = feld
        self.font_size = 18
        self.row_size = 20
        self.col_size = 9
        self.set_size_request(self.get_preferred_width()[0], self.get_preferred_height()[0])
        self.connect("draw", self.draw_feld)
    
    def draw_feld(self, _self, ct: cairo.Context):
        rs = self.row_size
        
        ct.select_font_face("Monospaced", cairo.FontSlant.NORMAL,
                            cairo.FontWeight.NORMAL)
        ct.set_font_size(self.font_size)
        ct.set_source_rgb(*self.BG)
        ct.paint()
        ct.set_source_rgb(*self.FG)
        y = rs
        if self.header:
            ct.move_to(0, rs)
            ct.show_text(self.header)
            y += rs
        
        for row in self.feld:
            for x, feld in enumerate(row):
                ct.move_to(x*self.col_size, y)
                if hasattr(feld, "draw"):
                    text, color = getattr(feld, 'draw')()
                    if color:
                        ct.set_source_rgb(*(c/255 for c in color))
                    else:
                        ct.set_source_rgb(*self.FG)
                    ct.show_text(text)
                else:
                    # ct.set_source_rgb(0,0,0)
                    ct.show_text(str(feld))
            y += rs
    
    def get_preferred_height(self):
        height = self.row_size * (bool(self.header) + len(self.feld))
        return height, height
    
    def get_preferred_width(self):
        width = self.col_size * max(len(f) for f in self.feld)
        return width, width
    
    def update(self, other: 'PixelArtDrawingArea'):
        self.feld = other.feld
        self.header = other.header
        self.set_size_request(self.get_preferred_width()[0], self.get_preferred_height()[0])
        self.queue_resize()

if __name__ == '__main__':
    from xwatc.scenario import Scenario, SCENARIO_ORT
    sc = Scenario.laden(SCENARIO_ORT + "/disnajenbun.txt")
    window = Gtk.Window()
    area = PixelArtDrawingArea(sc.anzeigename, sc.feld)
    window.add(area)
    window.set_default_size(area.get_preferred_width()[0], area.get_preferred_height()[0])
    window.show_all()
    window.connect("destroy", lambda *_args:Gtk.main_quit())
    Gtk.main()