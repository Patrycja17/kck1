# -*- coding: utf-8 -*-

from psychopy import visual, event, core
import multiprocessing as mp
import pygame as pg
import pandas as pd
import filterlib as flt
import blink as blk

pg.init()

# from pyOpenBCI import OpenBCIGanglion

note1_width = 1340
note2_width = 1072
note3_width = 804


def blinks_detector(quit_program, blink_det, blinks_num, blink, ):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        # print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                # connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()

    ####################################################
    SYMULACJA_SYGNALU = True
    ####################################################
    mac_adress = 'd2:b4:11:81:48:ad'
    ####################################################

    clock = pg.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)


if __name__ == "__main__":
    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    # connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
    )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')

    ############################################
    # Poniżej należy dodać rozwinięcie programu
    ############################################

    """
    level_select = gui.Dlg(title="pyRhytmics",
                           labelButtonOK="Start!",
                           labelButtonCancel="Quit",
                           )
    level_select.addText("Welcome to pyrhytmics!")
    level_select.addField("Select level: ", choices=["Easy", "Hard"])
    """
    win = visual.Window(
        size=[1280, 768],
        units="pix",
        fullscr=False
    )
    char_height = -134
    char_width = -400
    easybcgr = visual.ImageStim(win, image='resources/easybcgr.jpg')
    hardbcgr = visual.ImageStim(win, image='resources/hardbcgr.jpg')
    notesprite = visual.ImageStim(win, image='resources/note.png')
    char = visual.ImageStim(win, image='resources/char1.png', pos=(char_width, char_height))
    note1 = visual.ImageStim(win, image='resources/note.png', pos=(note1_width, 0))
    note2 = visual.ImageStim(win, image='resources/note.png', pos=(note2_width, 0))
    note3 = visual.ImageStim(win, image='resources/note.png', pos=(note3_width, 0))
    interval = 250


    def note1_movement():

        global note1_width
        if note1_width > 0:
            note1_width -= 268
            refresh_screen()
        else:
            note1_width = 1340
            refresh_screen()


    def note2_movement():
        global note1_width
        if note1_width > 0:
            note1_width -= 268
            refresh_screen()
        else:
            note1_width = 1340
            refresh_screen()


    def note3_movement():
        global note1_width
        if note1_width > 0:
            note1_width -= 268
            refresh_screen()
        else:
            note1_width = 1340
            refresh_screen()


    def notes_movement():
        move_side_event = pg.USEREVENT + 1
        pg.time.set_timer(move_side_event, 600)

        note1_movement()
        note2_movement()
        note3_movement()

    def charmovement():
        if blink.value == 1:
            print('BlINK')
            char.pos = (char_width, char_height + 134)
            refresh_screen()
            pg.time.wait(100)
            char.pos = (char_width, char_height)
            refresh_screen()
            blink.value = 0


    def refresh_screen():
        easybcgr.draw(win)
        char.draw(win)
        note1.draw(win)
        note2.draw(win)
        note3.draw(win)
        win.update()


    def game_loop():
        refresh_screen()
        notes_movement()
        charmovement()
        print(note1_width)
        refresh_screen()


    while True:
        game_loop()
        if 'escape' in event.getKeys():
            print('quitting')
            quit_program.set()
        if quit_program.is_set():
            break

    # Zakończenie podprocesów
    proc_blink_det.join()
