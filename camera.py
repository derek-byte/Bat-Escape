import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from random import randint
import time


class VideoCamera(object):

    def resetGhost(self):
        x_ghost = 50
        y_ghost = randint(50, 550)
        ghostPos = [x_ghost, y_ghost]
        return ghostPos

    def __init__(self):
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)

        self.num_ghost = 3

        for num in range(1, self.num_ghost):
            x_ghost = 50
            y_ghost = randint(50, 550)
            exec(f'self.ghostPos{num} = [{x_ghost}, {y_ghost}]')
            exec(f'x{num}, y{num} = self.resetGhost()')

        self.speedY = 50
        self.check_over = False
        self.win = False

        self.video = cv2.VideoCapture(0)
        self.video.set(3, 1280)
        self.video.set(4, 720)

        imgBackground = cv2.imread("Resources/background.jpg")
        ghost = cv2.imread(
            "Resources/ghost.png", cv2.IMREAD_UNCHANGED)
        bat = cv2.imread("Resources/bat.png", cv2.IMREAD_UNCHANGED)
        game_over = cv2.imread("Resources/game_over.png")
        win_background = cv2.imread("Resources/win.png")

        self.background_resized = cv2.resize(
            imgBackground, (1280, 720), interpolation=cv2.INTER_AREA)
        self.bat_resized1 = cv2.resize(
            bat, (60, 65), interpolation=cv2.INTER_AREA)
        self.ghost_resized = cv2.resize(
            ghost, (96, 96), interpolation=cv2.INTER_AREA)
        self.game_over_resized = cv2.resize(
            game_over, (1280, 720), interpolation=cv2.INTER_AREA)
        self.winner_resized = cv2.resize(
            win_background, (1280, 720), interpolation=cv2.INTER_AREA)

        self.t0 = time.time()

        self.increasing_timer = 0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        _, self.img = self.video.read()

        self.img = cv2.flip(self.img, 1)

        imgRaw = self.img.copy()

        hands, self.img = self.detector.findHands(self.img, flipType=False)

        self.img = cv2.addWeighted(
            self.img, 0.2, self.background_resized, 0.8, 0.0)

        if hands:
            for hand in hands:
                x, y, w, h, = hand['bbox']

                h1, w1, _ = self.bat_resized1.shape
                x_hand = x - w1//2
                y_hand = y - h1//2
                x_hand = np.clip(x_hand, 100, 1140)
                y_hand = np.clip(y_hand, 100, 700)

                if hand['type'] == "Right":
                    self.img = cvzone.overlayPNG(
                        self.img, self.bat_resized1, (x_hand, y_hand))

                    for num in range(1, self.num_ghost):
                        exec(
                            f'if (x_hand-w1) < self.ghostPos{num}[0] < x_hand + w1 and (y_hand-h1) < self.ghostPos{num}[1] < y_hand + h1: self.check_over = True')
        else:
            try:
                self.img = cvzone.overlayPNG(
                    self.img, self.bat_resized1, (x_hand, y_hand))
            except:
                pass

        if self.check_over:
            if self.win == True:
                self.img = cv2.addWeighted(
                    self.winner_resized, 0.8, self.background_resized, 0.2, 0.0)
            else:
                self.img = cv2.addWeighted(
                    self.game_over_resized, 0.8, self.background_resized, 0.2, 0.0)

        else:
            for num in range(1, self.num_ghost):
                exec(
                    f'if self.ghostPos{num}[0] <= 1100 and self.ghostPos{num}[1] >= 50: self.ghostPos{num}[0] += self.speedY')
                exec(
                    f'self.img = cvzone.overlayPNG(self.img, self.ghost_resized, self.ghostPos{num})')

            for num in range(1, self.num_ghost):
                exec(f'x{num}, y{num} = self.resetGhost()')
                exec(
                    f'if self.ghostPos{num}[0] == (1100 + x{num}):self.ghostPos{num}[1], self.ghostPos{num}[0] = y{num}, x{num}')

            t1 = time.time()
            total = t1-self.t0
            self.seconds = int(total)

            cv2.putText(self.img, "Time: "+str(self.seconds), (1100, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if self.win == True:
                cv2.putText(self.img, "WINNER", (1100, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 172, 28), 2)
            cv2.putText(self.img, "Press [r] to restart", (1025, 700),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            if self.seconds % 5 == 0 and self.increasing_timer == 0:
                self.increasing_timer += 1

            if self.seconds == 30:
                self.win = True

            increasing_amount = 1
            if self.seconds % 5 != 0 and self.increasing_timer == 1:
                self.num_ghost += increasing_amount
                self.increasing_timer = 0

                for num in range(self.num_ghost-increasing_amount, self.num_ghost):
                    x_ghost = 50
                    y_ghost = randint(50, 550)
                    exec(f'self.ghostPos{num} = [{x_ghost}, {y_ghost}]')
                    exec(f'x{num}, y{num} = self.resetGhost()')
        self.img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

        cv2.imshow("Image", self.img)
        key = cv2.waitKey(1)

        if key == ord("r"):
            for num in range(1, self.num_ghost):
                exec(f'x{num}, y{num} = self.resetGhost()')
                exec(f'self.ghostPos{num} = [x{num}, y{num}]')

            self.num_ghost = 3
            self.t0 = time.time()
            self.speedY = 50
            self.check_over = False

        _, jpeg = cv2.imencode('.jpg', self.img)
        return jpeg.tobytes()
