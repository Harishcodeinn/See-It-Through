import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import speech_recognition as sr
import pyttsx3
import datetime
import threading

class VoiceReminder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.engine = pyttsx3.init()
        self.reminder_event = None
        self.reminder_message = ''
        self.reminder_thread = None
        self.engine.startLoop(False)

        self.start_button = Button(text='Start Recording', on_press=self.start_recording)
        self.label = Label(text='')
        self.add_widget(self.start_button)
        self.add_widget(self.label)

    def start_recording(self, instance):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.label.text = 'Listening...'
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            self.handle_voice_input(text)
        except sr.UnknownValueError:
            self.label.text = 'Could not understand audio'
        except sr.RequestError as e:
            self.label.text = f'Speech recognition error: {e}'

    def handle_voice_input(self, text):
        reminder_regex = r'remind\s+me\s+(.+)\s+at\s+(\d+)\s*[:ap.m]*\s*(\d+)?'
        matches = re.match(reminder_regex, text, re.IGNORECASE)
        if matches:
            self.reminder_message = matches.group(1)
            hour = int(matches.group(2))
            minute = int(matches.group(3)) if matches.group(3) else 0
            self.schedule_reminder(hour, minute)
        else:
            self.label.text = 'Invalid reminder command'

    def schedule_reminder(self, hour, minute):
        now = datetime.datetime.now()
        reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if reminder_time < now:
            reminder_time += datetime.timedelta(days=1)
        delay = (reminder_time - now).total_seconds()
        if self.reminder_event:
            self.reminder_event.cancel()
        self.reminder_event = Clock.schedule_once(self.trigger_reminder, delay)
        self.label.text = f'Reminder set for {reminder_time.strftime("%I:%M %p")}'

    def trigger_reminder(self, dt):
        self.label.text = 'Reminder:'
        self.reminder_thread = threading.Thread(target=self.play_reminder_message)
        self.reminder_thread.start()

    def play_reminder_message(self):
        while True:
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(minutes=2)
            while datetime.datetime.now() < end_time:
                self.engine.say(self.reminder_message)
                self.engine.iterate()
            self.engine.endLoop()
            stop_time = datetime.datetime.now()
            off_time = stop_time + datetime.timedelta(seconds=5)
            while datetime.datetime.now() < off_time:
                pass
            self.engine.startLoop(False)

class VoiceReminderApp(App):
    def build(self):
        return VoiceReminder()

if __name__ == '__main__':
    VoiceReminderApp().run()