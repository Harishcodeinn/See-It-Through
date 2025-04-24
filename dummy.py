import speech_recognition as sr
import pyttsx3
import smtplib
import threading
import datetime
import cv2
import re
import numpy as np
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

class VoiceReminder:
    def __init__(self, message):
        self.message = message
        self.engine = pyttsx3.init()

    def trigger_reminder(self):
        reminder_thread = threading.Thread(target=self._repeat_sound)
        reminder_thread.start()

    def _repeat_sound(self):
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=2)
        while datetime.datetime.now() < end_time:
            self.engine.say(self.message)
            self.engine.runAndWait()
        self.engine.stop()

class VoiceEmailApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.unm = "harishptce@gmail.com"
        self.pwd = "umox qonp ukik krnn"

        self.layout = BoxLayout(orientation='vertical')

        self.reminder_button = Button(text='Reminder', on_press=self.start_reminder)
        self.object_detect_button = Button(text='Object Detection', on_press=self.open_camera)
        self.email_button = Button(text='Voice Mail', on_press=self.perform_action)
        self.label = Label(text='See It Through')

        self.layout.add_widget(self.reminder_button)
        self.layout.add_widget(self.object_detect_button)
        self.layout.add_widget(self.email_button)
        self.layout.add_widget(self.label)

        self.reminder_thread = None
        self.vs = None
        self.fps = None
        self.net = None



    def build(self):
        return self.layout

    def speak(self, text):
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.speak("Speak Now:")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                self.speak("Sorry, could not recognize what you said")
                return ""
            except sr.RequestError as e:
                self.speak("Could not request results from Google Speech Recognition service.")
                return ""

    def perform_action(self, instance):
        self.speak("What do you want to do? Speak MAIL to Send mail, Speak READ to Read Inbox, Speak REMINDER to Start Reminder, Speak OBJECT to Start Object Detection, Speak EXIT to Exit")

        choice = self.listen().lower()

        if choice == 'mail':
            self.send_email()
        elif choice == 'read':
            self.read_email()
        elif choice == 'reminder':
            self.start_reminder(None)
        elif choice == 'object':
            self.open_camera(None)
        elif choice == 'exit':
            self.stop()
        else:
            self.speak("Invalid choice. Please try again.")
            self.perform_action()

    def send_email(self):
        def remove(string):
            return ''.join(e for e in string if e.isalnum())

        def sendmail():
            unm = "harishptce@gmail.com"
            pwd = "umox qonp ukik krnn"
            str = "Please provide Receiver's mail id"
            self.speak(str)

            id = self.listen().lower()
            id1 = remove(id)
            id2 = "@gmail.com"
            rec1 = id1 + id2
            rec = rec1

            print(rec)
            str = "Please speak the body of your email"
            self.speak(str)

            msg = self.listen()

            str = "You have spoken the message"
            self.speak(str)
            self.speak(msg)

            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(unm, pwd)
            server.sendmail(unm, rec, msg)
            server.quit()

            str = "The email has been sent"
            self.speak(str)

        sendmail()


    def read_email(self):
        self.speak("Reading email functionality is not implemented yet.")

    def start_reminder(self, instance):
        self.label.text = 'Reminder functionality activated'
        if self.vs:
            self.vs.stop()
        if self.fps:
            self.fps.stop()
        if self.reminder_thread:
            self.reminder_thread.cancel()
        if self.net:
            cv2.destroyAllWindows()
        self.vs = None
        self.fps = None
        self.reminder_thread = threading.Thread(target=self.run_reminder)
        self.reminder_thread.start()

    def run_reminder(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.label.text = 'Listening...'
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            matches = re.search(r'remind me to (.+) at (\d+):(\d+)', text)
            if matches:
                message = matches.group(1)
                hour = int(matches.group(2))
                minute = int(matches.group(3))
                now = datetime.datetime.now()
                reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if reminder_time < now:
                    reminder_time += datetime.timedelta(days=1)
                delay = (reminder_time - now).total_seconds()
                Clock.schedule_once(lambda dt: self.trigger_reminder(reminder_time, message), delay)
                self.label.text = f'Reminder set for {reminder_time.strftime("%I:%M %p")}'
                timestr=f'Reminder set for {reminder_time.strftime("%I:%M %p")}'
                self.speak(timestr)
            else:
                self.label.text = 'Invalid reminder command'
                self.speak("Invalid reminder command")
                self.reminder_thread = threading.Thread(target=self.run_reminder)
                self.reminder_thread.start()
        except sr.UnknownValueError:
            self.label.text = 'Could not understand audio'
        except sr.RequestError as e:
            self.label.text = f'Speech recognition error: {e}'

    def trigger_reminder(self, reminder_time, message):
        reminder = VoiceReminder(message)
        reminder.trigger_reminder()

    def open_camera(self, instance):
        self.speak("Camera opened")

        thres = 0.60  # Confidence threshold for object detection
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        cap.set(10, 70)

        classNames = []
        classFile = r"D:\python\sig\coco.names"
        with open(classFile, "rt") as f:
            classNames = f.read().rstrip('\n').split('\n')

        configPath = r"D:\python\sig\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        weightsPath = r"D:\python\sig\frozen_inference_graph.pb"

        net = cv2.dnn_DetectionModel(weightsPath, configPath)
        net.setInputSize(320, 320)
        net.setInputScale(1.0 / 127.5)
        net.setInputMean((127.5, 127.5, 127.5))
        net.setInputSwapRB(True)

        while True:
            success, img = cap.read()
            if not success:
                break

            classIds, confs, bbox = net.detect(img, confThreshold=thres)

            if len(classIds) != 0:
                for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                    detected_object = classNames[classId - 1]
                    print(detected_object)
                    self.speak(f"{detected_object} detected")

                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, detected_object.upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Output', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def on_stop(self):
        if self.vs:
            self.vs.stop()
        if self.fps:
            self.fps.stop()
        if self.reminder_thread:
            self.reminder_thread.cancel()
        if self.net:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    VoiceEmailApp().run()
