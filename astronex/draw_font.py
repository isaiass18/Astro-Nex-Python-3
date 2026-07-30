import cairo

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 200)
cr = cairo.Context(surface)
cr.set_source_rgb(1, 1, 1)
cr.paint()
cr.set_source_rgb(0, 0, 0)
cr.select_font_face('Astro-Nex')
cr.set_font_size(40)

cr.move_to(10, 40)
cr.show_text("q w e r t y u i o p a s")

cr.move_to(10, 90)
cr.show_text("Q W E R T Y U I O P A S")

cr.move_to(10, 140)
cr.show_text("a s d f g h j k l z x c")

surface.write_to_png('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/font_test.png')
