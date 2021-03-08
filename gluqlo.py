# yet incomplete translation of: https://github.com/alexanderk23/gluqlo
from datetime import datetime
import pygame
import math
import os


try:
    _dir = os.path.dirname(os.path.abspath(__file__))
except:  ## __file__ doesn't exists in py2exe context
    __file__=os.getcwd()
    _dir = os.path.abspath(__file__)


os.environ['SDL_VIDEODRIVER']='windib'


FONT_COLOR = 0xb7, 0xb7, 0xb7
BACKGROUND_COLOR = 0x0f, 0x0f, 0x0f

SQRT2 = math.sqrt(2)

def fill_surface(surf, coords4, r, color):
    rpsqrt = int(r/SQRT2)
    _x, _y, _w, _h = coords4
    _w = int(_w//2) -1
    _h = int(_h//2) -1

    x0 = _x + _w
    y0 = _y + _h

    _w -= r
    _h -= r
    if (_w<=0) or (_h<=0):
        return

    sy = y0 - _h
    ey = y0 + _h
    sx = x0 - _w
    ex = x0 + _w

    surf.lock()
    try:
        for i in range(int(sy), int(ey)):
            for j in range(int(sx-r), int(ex+r+1)):
                surf.set_at((j,i), color)
        d = -r
        x2m1 = -1
        y = r

        for x in range(rpsqrt+1):
            x2m1 += 2
            d += x2m1
            if d>=0:
                y-=1
                d-=y*2

            for i in range(int(sx-y),int(ex+y)):
                surf.set_at((i, int(sy-x)), color)
                surf.set_at((i, int(ey+x)), color)
                
            for i in range(int(sx-x),int(ex+x)):
                surf.set_at((i, int(sy-y)), color)
                surf.set_at((i, int(ey+y)), color)
    finally:
        surf.unlock()


pygame.init()
pygame.display.init()
try:
    screen = pygame.display.set_mode((0,0), flags=pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
except:
    screen = pygame.display.set_mode((0,0), pygame.DOUBLEBUF|pygame.FULLSCREEN)
width, height = screen.get_width(), screen.get_height()
clock = pygame.time.Clock()
done = False

font_filename = os.path.join(_dir, 'gluqlo.ttf')
font_time = pygame.font.Font(font_filename, int(height / 1.68))

past_h = 99
past_m = 99
_24hs = True
leadingZero = True
rectsize = height * 0.6
spacing = width * 0.031
radius =  height * 0.05714
jitter_width =jitter_height = 1
# if display_scale_factor != 1:
# 	jitter_width  = (screen->w - width) * 0.5;
# 	jitter_height = (screen->h - height) * 0.5;

hourBackground_x = 0.5 * (width - (0.031 * width) - (1.2 * height)) + jitter_width
hourBackground_y = 0.2 * height + jitter_height
hourBackground_w = hourBackground_h = rectsize
hourBackground = list(map(int, [hourBackground_x, hourBackground_y, hourBackground_w, hourBackground_h]))
minBackground = list(map(int, [hourBackground[0]+(spacing+(0.6*height)), hourBackground[1], rectsize, rectsize ]))


def blig_digits(surf, bg_rect, spc, digits, color):
    adjust_x = 2.5*spc if (digits[0]=='1') else 0
    center_x = int(bg_rect[0] + bg_rect[2]/2 - adjust_x)
    if len(digits)>1:
        #TTF_GlyphMetrics(font_time, digits[0], &min_x, &max_x, &min_y, &max_y, &advance);
        minx, maxx, miny, maxy, advance = font_time.metrics(digits[0])[0]
        s1 = font_time.render(digits[0], True, color)
        x = center_x-maxx+minx-spc-(spc if adjust_x else 0)
        y = bg_rect[1]+int((bg_rect[3]-s1.get_height())/2)
        surf.blit(s1, (int(x),int(y)))
# 		// second digit
# 		TTF_GlyphMetrics(font_time, digits[1], &min_x, &max_x, &min_y, &max_y, &advance);
        minx, maxx, miny, maxy, advance = font_time.metrics(digits[1])[0]
# 		glyph = TTF_RenderGlyph_Blended(font_time, digits[1], color);
        s1 = font_time.render(digits[1], True, color)
# 		coords.y = rect->y + (rect->h - glyph->h) / 2;
# 		coords.x = center_x + spc / 2;
        y = bg_rect[1]+int((bg_rect[3]-s1.get_height())/2)
        x = center_x+ int(spc/2)
# 		SDL_BlitSurface(glyph, 0, surface, &coords);
        surf.blit(s1, (int(x),int(y)))
# 		SDL_FreeSurface(glyph);
    else:
        s1 = font_time.render(digits[0], True, color)
        x = center_x - int(s1.get_width()/2)
        y = bg_rect[1] + int((bg_rect[3]-s1.get_height())/2)
        surf.blit(s1, (x,y))


def render_digits(surf, bg_rect, bg, digits, prevdigits, maxsteps, steps):
    spc = surf.get_height() * 0.0125
    rect = bg_rect[:]
    rect[-1] = rect[-1]//2
    rect = list(map(int, rect))

	# SDL_SetClipRect(surface, &rect);
	# SDL_BlitSurface(bg, 0, surface, &rect);
	# blit_digits(surface, background, spc, digits, FONT_COLOR);
	# SDL_SetClipRect(surface, NULL);
    surf.set_clip(rect)
    surf.blit(bg, rect)
    blig_digits(surf, bg_rect, spc, digits, FONT_COLOR)
    surf.set_clip(None)

	# int halfsteps = maxsteps / 2;
	# int upperhalf = (step+1) <= halfsteps;
	# if(upperhalf) {
	# 	scale = 1.0 - (1.0 * step) / (halfsteps - 1);
	# 	c = 0xb7 - 0xb7 * (1.0 * step) / (halfsteps - 1);
	# } else {
	# 	scale = ((1.0 * step) - halfsteps + 1) / halfsteps;
	# 	c = 0xb7 * ((1.0 * step) - halfsteps + 1) / halfsteps;
	# }
	# color.r = color.g = color.b = c;
    halfsteps = maxsteps/2
    upperhalf = (steps+1)<=halfsteps
    if upperhalf:
        P = lambda x: x - (x*1.0*steps)/(halfsteps-1)
    else:
        P = lambda x: x*(((1.0*steps)-halfsteps+1)/halfsteps)
    scale = P(1.0)
    c = P(0xb7)
    color = int(c), int(c), int(c)
    
	# // create surface to scale from filled background surface
	# SDL_Surface *bgcopy = SDL_ConvertSurface(bg, bg->format, bg->flags);
	# rect.x = 0;
	# rect.y = 0;
	# rect.w = bgcopy->w;
	# rect.h = bgcopy->h;
	# blit_digits(bgcopy, &rect, spc, upperhalf ? prevdigits : digits, color);
    bgcopy = bg.convert()
    rect[0] = rect[1] = 0
    rect[2] = bgcopy.get_width()
    rect[3] = bgcopy.get_height()
    blig_digits(bgcopy, rect, spc, prevdigits if upperhalf else digits, color)

	# // scale and blend it to dest
	# SDL_Surface *scaled = zoomSurface(bgcopy, 1.0, scale, 1);
	# rect.x = 0;
	# rect.y = upperhalf ? 0 : scaled->h / 2;
	# rect.w = scaled->w;
	# rect.h = scaled->h / 2;
	# dstrect.x = background->x;
	# dstrect.y = background->y + ( upperhalf ? ((background->h - scaled->h) / 2) : background->h / 2);
	# dstrect.w = rect.w;
	# dstrect.h = rect.h;	
	# SDL_SetClipRect(surface, &dstrect);
	# SDL_BlitSurface(scaled, &rect, surface, &dstrect);
	# SDL_SetClipRect(surface, NULL);
	# SDL_FreeSurface(scaled);
	# SDL_FreeSurface(bgcopy);
    ## py:
    #upperhalf = False
    ww, hh = bgcopy.get_width(), bgcopy.get_height()
    #print('scale:', scale)
    scaled = pygame.transform.smoothscale(bgcopy, (ww, int(hh*scale)))
    scaled_h = scaled.get_height()
    scaled_h2 = int(scaled_h/2)
    rect = [0, 0 if upperhalf else scaled_h2, scaled.get_width(), scaled_h2]
    #print("bg: ",ww, hh, " scaled:", scaled.get_width(), scaled_h)
    #print("rect: ",rect)
    dst_y = (bg_rect[3]-scaled_h) if upperhalf else bg_rect[3]
    dstrect = list(map(int, [bg_rect[0], bg_rect[1]+(dst_y/2), rect[2], rect[3]]))
    surf.set_clip(dstrect)
    surf.blit(scaled, dstrect, area=rect)
    surf.set_clip(None)

	# # // draw divider
    rect2 = list(map(int, [bg_rect[0], bg_rect[1]+(bg_rect[3]-(surf.get_height() * 0.005))/2, bg_rect[2], surf.get_height() * 0.005]))
	# # rect.h = surface->h * 0.005;
	# # rect.w = background->w;
	# # rect.x = background->x;
	# # rect.y = background->y + (background->h - rect.h) / 2;
	# # SDL_FillRect(surface, &rect, SDL_MapRGB(surface->format, 0, 0, 0));
    #print(111,rect2)
    fill_surface(surf, rect2, radius, BACKGROUND_COLOR)
	# rect.y += rect.h;
	# rect.h = 1;
	# SDL_FillRect(surface, &rect, SDL_MapRGB(surface->format, 0x1a, 0x1a, 0x1a));
    rect2[1]+=rect2[3]
    rect2[3]=20
    #print(222,rect2)
    fill_surface(surf, rect2, radius, (0x1a,0x00,0x00, 0xff))


def render_clock(bg, maxsteps, steps, hour, minute):
    global past_h, past_m
    if hour!=past_h:
        h = hour if _24hs else (((hour+11)%12)+1)
        F = '%02d' if leadingZero else '%d'
        buffer = F%h
        buffer2 = F%past_h
        render_digits(screen, hourBackground, bg, buffer, buffer2, maxsteps, steps)

    if minute!=past_m:
        buffer = '%02d'%minute
        buffer2 = '%02d'%past_m
        render_digits(screen, minBackground, bg, buffer, buffer2, maxsteps, steps)
        pygame.display.flip()

    if steps == maxsteps-1:
        past_h = hour
        past_m = minute


def render_animate(bg):
    dt = datetime.now()
    if not True:
        return render_clock(bg, 20, 19, dt.hour, dt.minute)

    duration = 200
    start = pygame.time.get_ticks()
    end = start + duration
    done = False
    while not done:
        current = pygame.time.get_ticks()
        if current>=end:
            done = 1
            current = end
        frame = 99 * (current-start) / (end-start)
        render_clock(bg, 100, frame, dt.hour, dt.minute)


def main():
    done = False
    screen.fill((0,0,0))
    bg_rect = 0, 0, rectsize, rectsize
    bg = pygame.Surface((int(rectsize), int(rectsize)), pygame.HWSURFACE|pygame.SRCALPHA) #, 32)
    fill_surface(bg, bg_rect, radius, BACKGROUND_COLOR)

    while not done:
        render_animate(bg)
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.K_ESCAPE, pygame.QUIT):
                done = True
        
        clock.tick(30)

main()
