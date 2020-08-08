#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main file to handle all UI coding and Kivy objects"""

import virtual_ensemble as vmet

#General Imports
import numpy as np
import cv2
import math
import random
import sys
from scipy import ndimage
import os
import time
import subprocess
import moviepy.editor as mp
import subprocess
import threading
from functools import partial
from tinydb import TinyDB, Query
from multiprocessing import Process

#Kivy import
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.dropdown  import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy. uix . button  import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.video import Video
from kivy.uix.image import Image, AsyncImage
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import ButtonBehavior
from kivy.uix.actionbar import ActionBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock


#-------------------------------------------------------------------------------
#------------------------------------KIVY---------------------------------------
#-------------------------------------------------------------------------------
global FILES
FILES = []
#global IMG_COUNT
IMG_COUNT = 0
CURRENT = ''

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

db = TinyDB('./db.json')

class CustomDropDown(DropDown):
    pass

class CustomButton(Button):
    pass

class Logo(BoxLayout):
    pass

class VidScreen(Screen):

    def stop_video(self):
        self.vid.state = 'stop'

    def play_on_enter(self, vidname):
        self.vid = VideoPlayer(source=vidname, state='play',
                            options={'allow_stretch':False,
                                    'eos': 'loop'})
        popup = Popup(title=vidname, content=self.vid)
        popup.bind(on_dismiss=lambda x:self.stop_video())
        popup.open()
        #self.add_widget(self.vid)

    def get_vidname(self, vidname):
        return vidname


#file chooser class
class FileChooser(BoxLayout):
    def selected(self, filename):
        try:
            self.ids.video.source = filename[0]
        except: pass

class ProjScreen(Screen):

    def on_enter(self):
        self.titlelabel = Label(color = (0,0,0,1), size_hint_x = 0.1, size_hint_y = 0.1, pos_hint = {'x':0.5, 'top':1})
        self.titlelabel.text = self.manager.current
        self.add_widget(self.titlelabel)

    def __init__(self, **kwargs):
        super(ProjScreen, self).__init__(**kwargs)
        self.dropdown = CustomDropDown()
        self.dropdown.bind(on_select = self.callback)
        self.current_pos_x = 0.077
        self.current_pos_y = 0.55
        self.mythread = threading.Thread(target=self.run_main)

        self.table = db.table(self.id)
        self.img_count = 0

        Clock.schedule_once(lambda *args: self.load())

    def load(self):
        for item in self.table.all():
            self.loadVideo(item['filename'])

    def testProgressBar(self):
        self.progBar = ProgressBar()
        self.actionlab = Label(size_hint_y = 0.2)
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(self.actionlab)
        layout.add_widget(self.progBar)
        cancelButton = Button(text = "Cancel", size_hint_x = 0.3, size_hint_y = 0.5,
                        pos_hint={'bottom':1, 'right':1})
        cancelButton.bind(on_press= lambda x:self.cancelRender())
        layout.add_widget(cancelButton)
        # buttonLayout = BoxLayout(orientation = 'horizontal', size_hint = (1, 0.1))
        # closeButton = Button(text = "Close", size_hint_x = 0.3, size_hint_y = 0.95)
        # uploadButton = Button(text = "Upload", size_hint_x = 0.3, size_hint_y = 0.95)
        # buttonLayout.add_widget(closeButton)
        # buttonLayout.add_widget(uploadButton)
        self.loadingPop = Popup(title='Processing videos!', content=layout,
                        size_hint=(None,None), size=(500,500))
        self.loadingPop.open()
        self.loadingPop.bind(on_open = self.puopen)
        self.mythread.start()
        # self.p = Process(target=self.run_main)
        # self.p.start()
        #self.p.join()

    def cancelRender(self):
        self.loadingPop.dismiss()
        # self.progBar.value = 0
        # self.actionlab.text = "Resizing videos..."
        # self.p.terminate()
        self.pr.cancel()
        print("terminated")

    def puopen(self, instance):
        Clock.schedule_interval(self.next, 1 / 25)

    def next(self, instance):
        if self.progBar.value>= 100:
            return False
        self.progBar.value = vmet.PERCENT
        self.actionlab.text = vmet.ACTION

    def run_main(self):
        files = []
        for item in self.table.all():
            files.append(item['filename'])
        self.pr = vmet.Processor(files, self.img_count)
        filename = str(self.manager.current) + 'VirtualEnsemble' + '.mp4'
        self.pr.run_app(filename)
        vid = VideoPlayer(source='./'+filename, state='play',
                            options={'allow_stretch':False,
                                    'eos': 'loop'})
        finalPop = Popup(title=filename, content=vid,
                        size_hint=(None,None), size=(500,500))
        finalPop.bind(on_dismiss=lambda x:self.stop_video(vid))
        finalPop.open()

    def stop_video(self, vid):
        vid.state = 'stop'

    def onNextScreen(self, btn, filename):
        self.manager.vid_screen.play_on_enter(filename)

    def callback(self, instance, x):
        layout = FileChooser()
        buttonLayout = BoxLayout(orientation = 'horizontal', size_hint = (1, 0.1))
        closeButton = Button(text = "Close", size_hint_x = 0.3, size_hint_y = 0.95)
        uploadButton = Button(text = "Upload", size_hint_x = 0.3, size_hint_y = 0.95)
        buttonLayout.add_widget(closeButton)
        buttonLayout.add_widget(uploadButton)
        layout.add_widget(buttonLayout)
        popup = Popup(title ='Choose file',
                      content = layout,
                      size_hint =(None, None), size =(500, 500))
        popup.open()
        closeButton.bind(on_press = popup.dismiss)
        method = x
        uploadButton.bind(on_release = lambda x:self.addFile(layout.ids.filechooser.selection[0], method))

    #function to add selected video button to the layout
    def addFile(self, filename, method):
        global IMG_COUNT
        if (method == 'Video selected'):
            # file upload
            FILES.append(filename)
            vidname = os.path.basename(filename)
            self.table.insert({'filename': filename})
            newButton = Factory.CustomButton(id=vidname, text=vidname)

            # TODO: Create thumbnails

            newButton.bind(on_release = lambda x:self.onNextScreen(self, filename))
            self.ids.grid.add_widget(newButton)

            vidDropdown = DropDown(auto_width = False,width = 100)
            newButton.vidDropdown = vidDropdown
            btn = Button(text='Delete Video', size_hint_y=None, height=40, width = 100)
            btn.bind(on_press = lambda x:self.deleteFile(vidname))
            vidDropdown.add_widget(btn)
            IMG_COUNT += 1
            self.img_count += 1
        else:
            # folder upload
            for file in os.listdir(filename):
                if not file.startswith('.'):
                    fullname = filename + '/' + file
                    FILES.append(fullname)
                    vidname = os.path.basename(file)
                    self.table.insert({'filename': fullname})
                    newButton = Factory.CustomButton(id=vidname, text=vidname)
                    newButton.bind(on_release = lambda x, input = fullname:self.onNextScreen(self, input))
                    self.ids.grid.add_widget(newButton)
                    vidDropdown = DropDown(id=vidname, auto_width = False,width = 100)
                    newButton.vidDropdown = vidDropdown
                    btn = Button(id = vidname,text='Delete', size_hint_y=None, height=40)
                    #btn.bind(on_press = lambda x:self.deleteFile(vidname))
                    btn.bind(on_press = lambda x:self.deleteFile(vidname))
                    vidDropdown.add_widget(btn)

    def loadVideo(self, filename):
        vidname = os.path.basename(filename)
        newButton = Factory.CustomButton(id=filename, text=vidname)
        newButton.bind(on_release = lambda x:self.onNextScreen(self, filename))
        self.ids.grid.add_widget(newButton)

        vidDropdown = DropDown()
        newButton.vidDropdown = vidDropdown
        btn = Button(text='Delete', size_hint_y=None, height=40)
        btn.bind(on_press = lambda x:self.deleteFile(filename))
        vidDropdown.add_widget(btn)
        self.img_count += 1

    def deleteFile(self, vid):
        Video = Query()
        self.table.remove(Video.filename == vid)
        for child in self.ids.grid.children:
            if child.id == vid:
                self.ids.grid.remove_widget(child)
        self.img_count -= 1

class ProjectCreator(BoxLayout):
    # projectName = TextInput(text='Project Name:')
    # projectName.bind(on_text_validate=on_enter)
    pass

class ErrorHandler(BoxLayout):
    pass


class HomeScreen(Screen):

    def showPopup(self, instance):
        instructions = BoxLayout(orientation = 'vertical')
        instrtext = Label(text = 'Click the plus button to create a new project.')
        close = Button(text = "OK", size_hint_x = 0.3, size_hint_y = 0.1, pos_hint = {'x': 0.4, 'bottom':1})
        instructions.add_widget(instrtext)
        instructions.add_widget(close)
        instrpop = Popup(title = 'Welcome to Opus!', content = instructions, size_hint = (None, None), size=(400,400))
        instrpop.open()
        close.bind(on_press = instrpop.dismiss)

    def __init__(self, **kwargs):
        super(HomeScreen,self).__init__(**kwargs)
        logo=Logo()
        self.add_widget(logo)
        self.table = db.table('projects')
        Clock.schedule_once(lambda *args: self.load())
        Clock.schedule_once(self.showPopup, 0.5)

    def load(self):
        for item in self.table.all():
            self.loadProject(item['name'])

    def callback(self):
        layout = ProjectCreator()
        buttonLayout = BoxLayout(orientation = 'horizontal', size_hint = (1, 0.3))
        createButton = Button(text="Create", size_hint_x = 0.3, size_hint_y = 0.3,
                                pos_hint = {'x':0.5, 'bottom':1})
        cancelButton = Button(text="Cancel", size_hint_x = 0.3, size_hint_y = 0.3,
                                pos_hint = {'x':0, 'bottom':1})
        textInput = TextInput(size_hint_y = 0.15, hint_text = 'Name')
        buttonLayout.add_widget(createButton)
        buttonLayout.add_widget(cancelButton)
        layout.add_widget(textInput)
        layout.add_widget(buttonLayout)
        layout.background = 'orange.png'

        popup = Popup(title = 'Create New Project', content = layout,
                        size_hint = (None, None), size=(300,250))
        popup.open()
        cancelButton.bind(on_press=popup.dismiss)
        createButton.bind(on_release = lambda x:self.createProject(textInput.text, popup))

    def createProject(self, name, popup):
        # cannot have two projects with the same name!
        popup.dismiss()
        layout = ErrorHandler()
        duplicateProject = False
        for screen in self.manager.screens:
            if screen.id == name:
                duplicateProject = True
                message = Label(text='Project already exists!')
                layout.add_widget(message)
                errPop = Popup(title='Error', content=layout,
                                size_hint=(None,None), size=(300,100))
                errPop.open()

        if not duplicateProject:
            self.table.insert({'name': name})
            newButton = Factory.CustomProjectButton(id=name,text=name)
            newButton.bind(on_release=lambda x:self.onNextScreen(self, name))
            self.ids.maingrid.add_widget(newButton)

            vidDropdown = DropDown(auto_width = False,width = 100)
            newButton.vidDropdown = vidDropdown
            btn = Button(text='Delete Project', size_hint_y=None, height=40)
            btn.bind(on_press = lambda x:self.deleteProject(name))
            vidDropdown.add_widget(btn)

            newScreen = Factory.ProjScreen(id=name, name=name)
            self.manager.add_widget(newScreen)

    def loadProject(self, name):
        newButton = Factory.CustomProjectButton(id=name, text=name)
        newButton.bind(on_release=lambda x:self.onNextScreen(self, name))
        self.ids.maingrid.add_widget(newButton)

        vidDropdown = DropDown()
        newButton.vidDropdown = vidDropdown
        btn = Button(text='Delete Project', size_hint_y=None, height=40)
        btn.bind(on_press = lambda x:self.deleteProject(name))
        vidDropdown.add_widget(btn)

        newScreen = Factory.ProjScreen(id=name, name=name)
        self.manager.add_widget(newScreen)

    def deleteProject(self, name):
        Project = Query()
        self.table.remove(Project.name == name)

        db.drop_table(name)

        for child in self.ids.maingrid.children:
            if child.id == name:
                self.ids.maingrid.remove_widget(child)
        for screen in self.manager.screens:
            if screen.id == name:
                self.manager.remove_widget(screen)

    def onNextScreen(self, btn, name):
        global CURRENT
        self.manager.transition.direction = 'left'
        CURRENT = name
        self.manager.current = name


class Manager(ScreenManager):
    transition = NoTransition()
    proj_screen = ObjectProperty(None)
    vid_screen = ObjectProperty(None)
    home_screen = ObjectProperty(None)


    def __init__(self, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)
        self.list_of_prev_screens = []


class OPUSApp(App):
    # def run_main(self):
    #     pr.run_app()

    def build(self):
        # return dropdownDemo
        return Manager()


if __name__=="__main__":
    OPUSApp().run()
