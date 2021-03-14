from __future__ import print_function
# yet incomplete translation of: https://github.com/alexanderk23/gluqlo
from datetime import datetime
import math
import os
import sys

import pygame

try:
    _dir = os.path.dirname(os.path.abspath(__file__))
except:  ## __file__ doesn't exists in py2exe context
    _dir = os.path.dirname(os.path.abspath(sys.executable))


FONT_COLOR = 0xb7, 0xb7, 0xb7
BACKGROUND_COLOR = 0x0f, 0x0f, 0x0f

SQRT2 = math.sqrt(2)

TARGET_FPS = 60
DEBUG = False
ANIMATE = True
DURATION = 200


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



class Gluqlo:
    def show_globals(self):
        print('TARGET_FPS: %d' % TARGET_FPS)
        print('DEBUG: %r' % DEBUG)
        print('DURATION: %d' % DURATION)
    
    def check_unsupported_option(self, option):
        if option in sys.argv:
            print("unsupported option:", option)
            sys.exit(-1)

    def check_args(self):
        attrs = pygame.DOUBLEBUF
        if '/s' in sys.argv:
            attrs = attrs|pygame.FULLSCREEN
        if '/f' in sys.argv:
            attrs = attrs & (~pygame.FULLSCREEN)
        self.check_unsupported_option('/c')
        self.check_unsupported_option('/p')
        return attrs

    def pygame_init(self, attrs):
        pygame.init()
        try:
            pygame.display.init()
        except:
            # required for xp..
            os.environ['SDL_VIDEODRIVER']='windib'
            pygame.display.init()
 
        try:
            self.screen = pygame.display.set_mode((0,0), flags=pygame.HWSURFACE|attrs)
        except:
            self.screen = pygame.display.set_mode((0,0), attrs)
        self.width, self.height = self.screen.get_width(), self.screen.get_height()
        self.clock = pygame.time.Clock()

        font_filename = os.path.join(_dir, 'gluqlo.ttf')
        self.font_time = pygame.font.Font(font_filename, int(self.height / 1.68))

    def __init__(self):
        attrs = self.check_args()
        self.show_globals()
        self.pygame_init(attrs)

        # config
        self.past_h = self.past_m = 99
        self._24hs = True
        self.leadingZero = True

        # calculate
        self.rectsize = self.height * 0.6
        self.spacing = self.width * 0.031
        self.radius = self.height * 0.05714
        self.jitter_width = self.jitter_height = 1
        # if display_scale_factor != 1:
        # 	self.jitter_width  = (screen->w - width) * 0.5;
        # 	self.jitter_height = (screen->h - height) * 0.5;

        hourBackground_x = 0.5 * (self.width - (0.031 * self.width) - (1.2 * self.height)) + self.jitter_width
        hourBackground_y = 0.2 * self.height + self.jitter_height
        hourBackground_w = hourBackground_h = self.rectsize
        self.hourBackground = list(map(int, [hourBackground_x, hourBackground_y, hourBackground_w, hourBackground_h]))
        self.minBackground = list(map(int, 
                [self.hourBackground[0]+(self.spacing+(0.6*self.height)), self.hourBackground[1], self.rectsize, self.rectsize ]))

        # animation parameters
        self.start = self.end = None
        # animation frame counter and max
        self.cnt = self.maxcnt = 0


    def blit_digits(self, surf, bg_rect, spc, digits, color):
        adjust_x = 2.5*spc if (digits[0]=='1') else 0
        center_x = int(bg_rect[0] + bg_rect[2]/2 - adjust_x)
        if len(digits)>1:
            minx, maxx, miny, maxy, advance = self.font_time.metrics(digits[0])[0]
            s1 = self.font_time.render(digits[0], True, color)
            x = center_x-maxx+minx-spc-(spc if adjust_x else 0)
            y = bg_rect[1]+int((bg_rect[3]-s1.get_height())/2)
            surf.blit(s1, (int(x),int(y)))
    # 		// second digit
            minx, maxx, miny, maxy, advance = self.font_time.metrics(digits[1])[0]
            s1 = self.font_time.render(digits[1], True, color)
            y = bg_rect[1]+int((bg_rect[3]-s1.get_height())/2)
            x = center_x+ int(spc/2)
            surf.blit(s1, (int(x),int(y)))
        else:
            s1 = self.font_time.render(digits[0], True, color)
            x = center_x - int(s1.get_width()/2)
            y = bg_rect[1] + int((bg_rect[3]-s1.get_height())/2)
            surf.blit(s1, (x,y))


    def render_digits(self, surf, bg_rect, bg, digits, prevdigits, maxsteps, steps):
        spc = surf.get_height() * 0.0125
        rect = bg_rect[:]
        rect[-1] = rect[-1]//2
        rect = list(map(int, rect))

        # blit digits upper half
        surf.set_clip(rect)
        surf.blit(bg, rect)
        self.blit_digits(surf, bg_rect, spc, digits, FONT_COLOR)
        surf.set_clip(None)

        # translate step-info into scale & color constants
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
        # full digits blit
        bgcopy = bg.convert()
        rect[0] = rect[1] = 0
        rect[2] = bgcopy.get_width()
        rect[3] = bgcopy.get_height()
        self.blit_digits(bgcopy, rect, spc, prevdigits if upperhalf else digits, color)

        # // scale and blend it to dest
        ww, hh = bgcopy.get_width(), bgcopy.get_height()
        scaled = pygame.transform.smoothscale(bgcopy, (ww, int(hh*scale)))
        scaled_h = scaled.get_height()
        scaled_h2 = int(scaled_h/2)
        rect = [0, 0 if upperhalf else scaled_h2, scaled.get_width(), scaled_h2]
        dst_y = (bg_rect[3]-scaled_h) if upperhalf else bg_rect[3]
        dstrect = list(map(int, [bg_rect[0], bg_rect[1]+(dst_y/2), rect[2], rect[3]]))
        surf.set_clip(dstrect)
        surf.blit(scaled, dstrect, area=rect)
        surf.set_clip(None)

        # # // draw divider
        # rect2 = list(map(int, [bg_rect[0], bg_rect[1]+(bg_rect[3]-(surf.get_height() * 0.005))/2, bg_rect[2], surf.get_height() * 0.005]))
        # fill_surface(surf, rect2, self.radius, BACKGROUND_COLOR)
        # rect2[1] += rect2[3]
        # rect2[3] = 1
        # fill_surface(surf, rect2, self.radius, (0x1a,0x1a,0x1a, 0xff))


    def render_clock(self, bg, maxsteps, steps, hour, minute):
        if hour!=self.past_h:
            h = hour if self._24hs else (((hour+11)%12)+1)
            F = '%02d' if self.leadingZero else '%d'
            buffer = F%h
            buffer2 = F%self.past_h
            self.render_digits(self.screen, self.hourBackground, bg, buffer, buffer2, maxsteps, steps)

        if minute!=self.past_m:
            buffer = '%02d'%minute
            buffer2 = '%02d'%self.past_m
            self.render_digits(self.screen, self.minBackground, bg, buffer, buffer2, maxsteps, steps)
            pygame.display.flip()
            
        if steps == maxsteps-1:
            self.past_h = hour
            self.past_m = minute


    def render_animate(self, bg, a, b):
        current = pygame.time.get_ticks()

        frame = 99
        if self.start is None:
            if b!=self.past_m:
                # start animation
                self.start = current
                self.end = current+DURATION

        if not(self.start is None):
            if current>self.end:
                # current = self.end  # unnecessary
                self.end = self.start = None
            else:
                frame = (99.0 * (current-self.start)) / DURATION  # (self.end-self.start)

        common_frame = frame==99
        if not common_frame:
            self.cnt+=1
        else:
            self.maxcnt = self.cnt if self.cnt>self.maxcnt else self.maxcnt
            self.cnt = 0
        #print('frame:' if common_frame else "*** %d"%frame, "---",  self.start, current, self.end, "---", b, self.past_m)
        self.render_clock(bg, 100, frame, a, b)


    def main(self):
        global ANIMATE
        done = False
        self.screen.fill((0,0,0))
        bg_rect = 0, 0, self.rectsize, self.rectsize
        bg = pygame.Surface((int(self.rectsize), int(self.rectsize)), pygame.HWSURFACE|pygame.SRCALPHA)
        fill_surface(bg, bg_rect, self.radius, BACKGROUND_COLOR)

        self.clock.tick(TARGET_FPS)
        while not done:
            self.clock.tick(TARGET_FPS)
            dt = datetime.now()
            a, b = (dt.minute, dt.second) if DEBUG else (dt.hour, dt.minute)
            if ANIMATE:
                self.render_animate(bg, a, b)
            else:
                self.render_clock(bg, 20, 19, a, b)
            for event in pygame.event.get():
                done = event.type in (pygame.KEYDOWN, pygame.K_ESCAPE, pygame.QUIT)

def get_bool(name, default):
    QUOTES = '"', "'"
    if name in os.environ:
        value = os.environ.get(name, str(default)).lower()
        if value[0] in QUOTES:
            value = value[1:] 
        if value[-1] in QUOTES:
            value = value[:-1] 
        return value in ('y', 'yes', 's', 'si','true', 't', '1')
    return default

def get_int(name, default=None):
    if name in os.environ:
        value = os.environ.get(name, str(default))
        try:
            return int(value)
        except:
            print("Cannot interpret:", value, "as integer!")
    return default
    

if __name__=="__main__":
    _TARGET_FPS, _FPS = 'TARGET_FPS', 'FPS'
    _DEBUG = 'DEBUG'
    _DURATION = 'DURATION'
    _ANIMATE = 'ANIMATE'

    TARGET_FPS = get_int(_TARGET_FPS, get_int(_FPS, default=TARGET_FPS))
    DURATION = get_int(_DURATION, default=DURATION)
    DEBUG = get_bool(_DEBUG, DEBUG)
    ANIMATE = get_bool(_ANIMATE, ANIMATE)

    ss = Gluqlo()
    try:
        ss.main()
    finally:
        if DEBUG: print("total: ", ss.maxcnt)