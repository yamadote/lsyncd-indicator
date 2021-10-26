#!/usr/bin/env python3
import subprocess
import os
import time
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject
from threading import Thread

currpath = os.path.dirname(os.path.realpath(__file__))

def runs():
    try:
        string = subprocess.check_output(["tail", "-1", "/var/log/lsyncd/lsyncd.log"]).decode("utf-8")
        return "finished" in string.lower()
    except subprocess.CalledProcessError:
        pass

class Indicator():
    def __init__(self):
        self.app = 'show_proc'
        iconpath = currpath+"/green.png"
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())

        self.update = Thread(target=self.check_runs)
        self.update.setDaemon(True)
        self.update.start()     

    def update_icon(self, path):
        GObject.idle_add(
            self.indicator.set_icon,
            currpath+path,
            priority=GObject.PRIORITY_DEFAULT
            )   

    def check_runs(self):
        runs1 = ""
        while True:
            time.sleep(0.5)
            runs2 = runs()
            if runs1 != runs2:
                if runs2:
                    self.update_icon("/green.png")
                else:
                    self.update_icon("/purple.png")
            runs1 = runs2

    def create_menu(self):
        menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def stop(self, source):
        Gtk.main_quit()

Indicator()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()