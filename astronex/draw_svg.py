import cairo

surface = cairo.SVGSurface('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/font_test.svg', 800, 200)
cr = cairo.Context(surface)
cr.select_font_face('Astro-Nex')
cr.set_font_size(40)

cr.move_to(10, 40)
cr.show_text("q w e")

cr.move_to(10, 90)
cr.show_text("a s d")

surface.finish()
