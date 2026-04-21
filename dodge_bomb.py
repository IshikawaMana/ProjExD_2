import os
import sys
import pygame as pg
import random
import time
import math

WIDTH :int =1100
HEIGHT :int = 650
img03 = pg.image.load("ex2/fig/3.png")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct):
    if 0 <= rct.left and rct.right <= WIDTH:
        yoko = True 
    else:
        yoko = False

    if 0 <= rct.top and rct.bottom <= HEIGHT:
        tate = True 
    else:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    black = pg.Surface((WIDTH, HEIGHT))
    black.set_alpha(200)

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)
    cry_l = cry_img.get_rect()
    cry_l.center = (WIDTH//2 - 150, HEIGHT//2)

    cry_r = cry_img.get_rect()
    cry_r.center = (WIDTH//2 + 150, HEIGHT//2)

    font = pg.font.Font(None, 50)
    text = font.render("GAME OVER", True, (255, 255, 255))
    text_rect = text.get_rect(center=((WIDTH//2, HEIGHT//2)))

    screen.blit(black, (0, 0))
    screen.blit(cry_img, cry_l)
    screen.blit(cry_img, cry_r)
    screen.blit(text, text_rect)
    pg.display.update()

    pg.time.wait(5000)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = [] 
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    #左向き
    img_left = pg.transform.rotozoom(img03, 0, 0.9)
    #右向き
    img_right = pg.transform.flip(img_left, True, False)

    kk_imgs = {
        (-5,  0): img_left,                                  # 左
        (-5, -5): pg.transform.rotozoom(img_left, -45, 1.0), # 左上
        ( 0, -5): pg.transform.rotozoom(img_right, 90, 1.0),   # 上
        (+5, -5): pg.transform.rotozoom(img_right, 45, 1.0),   # 右上
        (+5,  0): img_right,                                   # 右
        (+5, +5): pg.transform.rotozoom(img_right, -45, 1.0),  # 右下
        ( 0, +5): pg.transform.rotozoom(img_right, -90, 1.0),  # 下
        (-5, +5): pg.transform.rotozoom(img_left, 45, 1.0),  # 左下
    }
    return kk_imgs

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    ox, oy = org.center
    dx, dy = dst.center

    # ベクトル
    vx = dx - ox
    vy = dy - oy

    # ノルム
    norm = (vx**2 + vy**2) * math.sqrt(1/2)

    if norm < 300:
        return current_xy

    # 正規化
    if norm != 0:
        vx = vx / norm * math.sqrt(50)
        vy = vy / norm * math.sqrt(50)

    return vx, vy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(img03, 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))
    bb_img.set_colorkey((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_rct = bb_img.get_rect()
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    
    vx = +5
    vy = +5
    clock = pg.time.Clock()
    tmr = 0

    bb_imgs, bb_accs = init_bb_imgs()
    kk_imgs = get_kk_imgs()
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()

        DELTA = {
            pg.K_UP:    (0, -5),
            pg.K_DOWN:  (0, +5),
            pg.K_LEFT:  (-5, 0),
            pg.K_RIGHT: (+5, 0),
        }

        sum_mv = [0, 0]
        for key, (dx, dy) in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += dx
                sum_mv[1] += dy
        
        mv = tuple(sum_mv)
        if mv in kk_imgs:
            kk_img = kk_imgs[mv]

        kk_rct.move_ip(sum_mv)

        bound = check_bound(kk_rct)
        yoko = bound[0]
        tate = bound[1]

        if yoko == False:
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        if tate == False:
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        bb_img = bb_imgs[min(tmr // 500, 9)]

        old_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = old_center

        # 追従ベクトルを計算
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        acc = bb_accs[min(tmr // 500, 9)]
        avx = vx * acc
        avy = vy * acc

        bb_rct.move_ip(avx, avy)


        bound = check_bound(bb_rct)
        bb_yoko = bound[0]
        bb_tate = bound[1]

        if bb_yoko == False:
            vx *= -1
        if bb_tate == False:
            vy *= -1

        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
