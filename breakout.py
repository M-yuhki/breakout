#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import math
import os
import sys
from operator import itemgetter
import random
import csv

SCR_RECT = Rect(0, 0, 372, 500)  # スクリーンのサイズ
# ゲーム状態
READY, PLAY, PAUSE, OPTION, CLEAR, GAMEOVER, RANKING = (0, 1, 2, 3, 4, 5, 6)
W = SCR_RECT.width
H = SCR_RECT.height
INPUT_RECT = Rect((W-300)/2, H/2-10, 300, 36)  # 文字入力ウィンドウのサイズ
FRAME = 60  # 1秒間に60回処理
RATE = 100  # スコア変換倍率
INIT_SCORE = 0  # 初期スコア
DEDUCTION = -5000  # 減点量
BONUSTIME = 180  # ボーナス発生時間(180秒以内)


class MyScreen:
    """画面状態表示"""
    # 画面表示共通の処理
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"BREAKOUT")

        # サウンドのロード
        Ball.paddle_sound = load_sound("wood00.wav")
        Ball.brick_sound = load_sound("chari06.wav")
        Ball.fall_sound = load_sound("fall06.wav")
        Ball.through_sound = load_sound("through.wav")
        Ball.levelup_sound = load_sound("levelup.wav")
        self.select_sound = load_sound("select.wav")

        # ゲームオブジェクトを初期化
        self.init_game(screen)
        # メインループ
        clock = pygame.time.Clock()
        while True:
            clock.tick(FRAME)
            self.draw(screen)
            self.update()
            pygame.display.update()
            self.key_handler(screen)

    def init_game(self, screen):
        """画面状態表示"""
        self.game_state = READY

        # フルスクリーンにするかどうかのフラグ
        self.fullscreen_flag = False

        # 1 周目のループか確認するためのフラグ(名前入力用)
        self.init_flag = True

        # スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()  # 描画用グループ
        self.bricks = pygame.sprite.Group()  # 衝突判定用グループ
        Paddle_left.containers = self.all
        Paddle_right.containers = self.all
        Ball.containers = self.all
        Brick.containers = self.all, self.bricks

        # ステージの決定
        self.stage = Stage()
        self.score = Score()
        self.paddle2_flag = False

        # ボタンを作成
        self.start_btn = Button(screen, 'START', (W/2-120, H/2, 110, 50))
        self.option_btn = Button(screen, 'OPTION', (W/2+10, H/2, 110, 50))
        self.return_btn = Button(screen, 'RETURN', (W/2-50, H/2+180, 100, 50))
        self.return_btn2 = Button(screen, 'RETURN', (W/2-50, H/2+180, 100, 50))
        self.stage_btn = Button(screen, 'NORMAL', (W/2-75, H/2-70, 150, 50))
        self.rank_btn = Button(screen, 'RANKING', (W/2-120, H/2+60, 240, 50))
        self.mode_btn = Button(screen, '1', (W/2-75, H/2+35, 150, 50))
        self.home_btn = Button(screen, 'HOME',  (W/2-50, H/2, 100, 50))

        # 入力読み取りウインドウ作成
        msg_engine = MessageEngine()
        self.input_wnd = InputWindow(INPUT_RECT, msg_engine)

        # ランキング作成
        self.list, Len, Rank = Ranking("", 0, 1)
        self.ranking_start = 0

    def update(self):
        """ゲーム状態の更新"""
        if self.game_state == PLAY:
            self.all.update()
            if len(Brick.containers[1]) == 0:  # ブロックがなくなったらクリア
                self.game_state = CLEAR
            if self.ball.life == 0:
                self.game_state = GAMEOVER

    def draw(self, screen):
        """画面描画"""

        # 画面を黒色にする
        screen.fill((0, 0, 0))

        title_font = pygame.font.Font(None, 55)  # タイトルフォント設定
        push_font = pygame.font.Font(None, 30)  # プッシュ文字フォント設定

        if self.game_state == READY:  # READY画面
            # タイトルを描画
            title = title_font.render("BREAKOUT", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, H/2-160))

            # PUSH SPACE を描画
            push_space = push_font.render("Push Space Key To Start",
                                          True, (255, 255, 255))
            screen.blit(push_space,
                        ((W-push_space.get_width())/2, H/2+120))

            # スタートボタンを描画
            self.start_btn.draw(screen)

            # option ボタンを描画
            self.option_btn.draw(screen)

            # ランキングボタンを描画
            self.rank_btn.draw(screen)

        elif self.game_state == PLAY:  # ゲームプレイ画面
            self.all.draw(screen)
            score_font = pygame.font.Font(None, 20)
            # スコアを描画
            score_moji = score_font.render(str(self.score.score),
                                           True, (255, 255, 255))
            screen.blit(score_moji,
                        ((W-score_moji.get_width())/2,
                         H-score_moji.get_height()))

        elif self.game_state == PAUSE:  # ポーズ画面
            # タイトルを描画
            title = title_font.render("PAUSE", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, 100))

            # home ボタンを描画
            self.home_btn.draw(screen)

            # PUSH SPACEを描画
            push_space = push_font.render("Push SPACE Key To Return",
                                          True, (255, 255, 255))
            screen.blit(push_space,
                        ((W-push_space.get_width())/2, H/2+150))

        elif self.game_state == OPTION:  # オプション画面
            # タイトルを描画
            title = title_font.render("OPTION", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, H/2-160))

            # タイトルを描画
            stage_moji = push_font.render("STAGE SELECT", True,
                                          (255, 255, 255))
            screen.blit(stage_moji, ((W-stage_moji.get_width())/2, H/2-100))

            # stage 選択ボタンを描画
            self.stage_btn.label_change(self.stage.stage[self.stage.select])
            self.stage_btn.draw(screen)

            # タイトルを描画
            stage_moji = push_font.render("PLAYER SELECT", True,
                                          (255, 255, 255))
            screen.blit(stage_moji, ((W-stage_moji.get_width())/2, H/2))

            # 人数選択ボタンを描画
            if self.paddle2_flag:
                self.mode_btn.label_change("2")
            else:
                self.mode_btn.label_change("1")
            self.mode_btn.draw(screen)
            # return ボタンを描画
            self.return_btn.draw(screen)

        elif self.game_state == RANKING:  # ランキング画面
            title = title_font.render("RANKING", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, H/2-160))
            # 上位ランカー表示
            Rank_Draw(screen, self.list, H/2-130, self.ranking_start, 10)
            # return ボタンを描画
            self.return_btn2.draw(screen)

        elif self.game_state == CLEAR:  # ゲームクリア画面
            # タイトルを描画
            title = title_font.render("GAME CLEAR", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, H/2-160))
            if self.init_flag:
                self.name = self.input_wnd.ask(screen, "NAME?:")
                self.list, self.Len, self.Rank = Ranking(self.name,
                                                         self.score.score, 0)
                Rank_Write(self.name, self.score.score)
                self.init_flag = False

            # スコア表示
            score_moji = push_font.render("NAME:" + self.name +
                                          "   SCORE:"+str(self.score.score),
                                          True, (255, 255, 255))
            screen.blit(score_moji,
                        ((W-score_moji.get_width())/2, H/2-160))

            font = pygame.font.Font(None, 25)
            r_moji = font.render("RANKING", True, (255, 0, 0))
            screen.blit(r_moji, ((W-r_moji.get_width())/2, H/2-60))

            # 上位ランカー表示
            Rank_Draw(screen, self.list, H/2-50, 0, 5)

            # ランキング表示
            rank_moji = push_font.render("YOUR RANK:  " + str(self.Rank) +
                                         " / "+str(self.Len),
                                         True, (255, 255, 255))
            screen.blit(rank_moji,
                        ((W-rank_moji.get_width())/2, H/2+130))

        elif self.game_state == GAMEOVER:  # ゲームオーバー画面
            # タイトルを描画
            title = title_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(title, ((W-title.get_width())/2, H/2-160))

            if self.init_flag:
                self.name = self.input_wnd.ask(screen, "NAME?:")
                self.list, self.Len, self.Rank = Ranking(self.name,
                                                         self.score.score, 0)
                Rank_Write(self.name, self.score.score)
                self.init_flag = False

            # スコア表示
            score_moji = push_font.render("NAME:" + self.name +
                                          "   SCORE:"+str(self.score.score),
                                          True, (255, 255, 255))
            screen.blit(score_moji,
                        ((W-score_moji.get_width())/2, H/2-100))

            font = pygame.font.Font(None, 25)
            r_moji = font.render("RANKING", True, (255, 0, 0))
            screen.blit(r_moji, ((W-r_moji.get_width())/2, H/2-60))

            # 上位ランカー表示
            Rank_Draw(screen, self.list, H/2-50, 0, 5)

            # ランキング表示
            rank_moji = push_font.render("YOUR RANK:  " + str(self.Rank) +
                                         " / "+str(self.Len),
                                         True, (255, 255, 255))
            screen.blit(rank_moji,
                        ((W-rank_moji.get_width())/2, H/2+130))

    def key_handler(self, screen):
        """キーハンドラー"""
        for event in pygame.event.get():
            # 閉じるボタンを押したとき
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # エスケープボタンを押したとき
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            # スペースを押したとき
            elif event.type == KEYDOWN and event.key == K_SPACE:
                # READY 画面の場合
                if self.game_state == READY:
                    self.stage.make_stage()
                    # パドル
                    if self.paddle2_flag:
                        paddle_left = Paddle_left("paddle_left.png")
                        paddle_right = Paddle_right("paddle_right.png")
                        self.ball = Ball(paddle_left, paddle_right,
                                         self.bricks, self.score)
                    else:
                        paddle_left = Paddle_right("paddle_left.png")
                        paddle_right = Paddle_right("paddle_left.png")
                        self.ball = Ball(paddle_left, paddle_right,
                                         self.bricks, self.score)
                    self.game_state = PLAY
                    self.select_sound.play()

                # プレイ画面の場合
                elif self.game_state == PLAY:
                    self.game_state = PAUSE

                # PAUSE 画面の場合
                elif self.game_state == PAUSE:
                    self.game_state = PLAY

                # オプション画面の場合
                elif self.game_state == OPTION:
                    self.game_state = READY

                # ランキング画面の場合
                elif self.game_state == RANKING:
                    self.game_state = READY

                # ゲームオーバー画面の場合
                elif self.game_state == GAMEOVER:
                    self.init_game(screen)  # ゲームを初期化
                    self.game_state = READY

                # ゲームクリア画面の場合
                elif self.game_state == CLEAR:
                    self.init_game(screen)  # ゲームを初期化
                    self.game_state = READY

            # F キーを押したとき
            elif event.type == KEYDOWN and event.key == K_f:
                # フルスクリーンフラグを切り替え
                self.fullscreen_flag = not self.fullscreen_flag
                if self.fullscreen_flag:
                    screen = pygame.display.set_mode(SCR_RECT.size, FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(SCR_RECT.size)

            # R キーを押したとき
            elif event.type == KEYDOWN and event.key == K_r:
                if self.game_state == PLAY:
                    self.game_state = GAMEOVER

            # 上キーを押したとき
            elif event.type == KEYDOWN and event.key == K_UP:
                if self.game_state == RANKING:
                    if self.ranking_start > 0:
                        self.ranking_start -= 1

            # 下キーを押したとき
            elif event.type == KEYDOWN and event.key == K_DOWN:
                if self.game_state == RANKING:
                    if self.ranking_start < len(self.list)-1:
                        self.ranking_start += 1

            # クリックしたとき
            elif event.type == pygame.MOUSEBUTTONUP:
                # READY 画面の場合
                if self.game_state == READY:
                    if self.start_btn.is_hover:
                        self.stage.make_stage()
                        # パドル
                        if self.paddle2_flag:
                            paddle_left = Paddle_left("paddle_left.png")
                            paddle_right = Paddle_right("paddle_right.png")
                            self.ball = Ball(paddle_left, paddle_right,
                                             self.bricks, self.score)
                        else:
                            paddle_left = Paddle_right("paddle_left.png")
                            paddle_right = Paddle_right("paddle_right.png")
                            self.ball = Ball(paddle_left, paddle_right,
                                             self.bricks, self.score)
                        self.game_state = PLAY
                        self.select_sound.play()

                    elif self.option_btn.is_hover:
                        self.game_state = OPTION
                        self.select_sound.play()

                    elif self.rank_btn.is_hover:
                        self.game_state = RANKING
                        self.select_sound.play()

                # オプション画面の場合
                elif self.game_state == OPTION:
                    if self.return_btn.is_hover:
                        self.game_state = READY

                # ポーズ画面の場合
                elif self.game_state == PAUSE:
                    if self.home_btn.is_hover:
                        self.init_game(screen)  # ゲームを初期化
                        self.game_state = READY

                # ランキング画面の場合
                elif self.game_state == RANKING:
                    if self.return_btn2.is_hover:
                        self.game_state = READY

            # クリックしたとき
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == OPTION:
                    if self.stage_btn.is_hover:
                        self.stage.Select()
                    if self.mode_btn.is_hover:
                        self.paddle2_flag = not self.paddle2_flag


class Stage:
    """ステージの選択"""
    def __init__(self):
        self.stage = ["NORMAL", "BORDER", "STRIPE",
                      "CHECK", "HEART", "SQUARE", "SPIRAL"]

        self.select = 0

    def Select(self):
        """セレクトボタン押された時"""
        if self.select == 6:
            self.select = 0
        else:
            self.select += 1

    def Read(self):
        """ステージ読み込み"""
        if self.select == 1:
            stage = open("data/border.csv", "rb")
            return csv.reader(stage)

        elif self.select == 2:
            stage = open("data/stripe.csv", "rb")
            return csv.reader(stage)

        elif self.select == 3:
            stage = open("data/check.csv", "rb")
            return csv.reader(stage)

        elif self.select == 4:
            stage = open("data/heart.csv", "rb")
            return csv.reader(stage)

        elif self.select == 5:
            stage = open("data/square.csv", "rb")
            return csv.reader(stage)

        elif self.select == 6:
            stage = open("data/spiral.csv", "rb")
            return csv.reader(stage)

        else:
            stage = open("data/normal.csv", "rb")
            return csv.reader(stage)

    def make_stage(self):
        dataReader = self.Read()

        # データに基づいたブロックの生成
        line_y = 1
        for row in dataReader:
            line_x = 1
            for data in row:
                if int(data) == 1:
                    Brick(line_x, line_y)
                line_x += 1
                if line_x >= 11:
                    break
            line_y += 1
            if line_y >= 11:
                break


class Button:
    """画面に表示するボタン"""

    def __init__(self, screen, text, rectcoord):
        self.is_hover = False
        self.default_color = (255, 255, 255)
        self.hover_color = (255, 128, 128)
        self.font_color = (255, 0, 0)
        self.font = pygame.font.Font(None, 30)
        self.label = self.font.render(text, 1, self.font_color)
        self.rectcoord = rectcoord

    def label_pos(self):
        """ラベルの位置をボタンの中央に表示"""
        return (self.obj.centerx-(self.label.get_width()/2),
                self.obj.centery-(self.label.get_height()/2))

    def color(self):
        """ホバー時カラー変更"""
        if self.is_hover:
            return self.hover_color
        else:
            return self.default_color

    def draw(self, screen):
        """ボタン描画"""
        try:
            self.check_hover()
        except:
            pass
        self.obj = pygame.draw.rect(screen, self.color(), self.rectcoord)
        screen.blit(self.label, self.label_pos())

    def check_hover(self):
        """ホバーチェック"""
        if self.obj.collidepoint(pygame.mouse.get_pos()):
            self.is_hover = True
        else:
            self.is_hover = False

    def label_change(self, text):
        self.label = self.font.render(text, 1, self.font_color)


class MessageEngine:
    """ウインドウにメッセージを表示"""
    def draw_string(self, screen, i_rect, str):
        """文字列を描画"""
        title_font = pygame.font.Font(None, 30)
        title = title_font.render(str, True, (255, 0, 0))
        screen.blit(title, (i_rect.x+5, i_rect.centery-(title.get_height()/2)))


class Window:
    """ウィンドウの基本クラス"""
    EDGE_WIDTH = 4  # 白枠の幅

    def __init__(self, rect):
        self.rect = rect  # 一番外側の白い矩形
        # 内側の黒い矩形
        self.inner_rect = self.rect.inflate(-self.EDGE_WIDTH*2,
                                            -self.EDGE_WIDTH*2)
        self.is_visible = False  # ウィンドウを表示中か？

    def draw(self, screen):
        """ウィンドウを描画"""
        if self.is_visible is False:
            return
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 0)
        pygame.draw.rect(screen, (100, 100, 100), self.inner_rect, 0)

    def show(self):
        """ウィンドウを表示"""
        self.is_visible = True

    def hide(self):
        """ウィンドウを隠す"""
        self.is_visible = False


class InputWindow(Window):
    """入力読み取りウインドウ作成"""
    def __init__(self, rect, msg_engine):
        Window.__init__(self, rect)
        self.msg_engine = msg_engine

    def get_key(self):
        """キー入力を読み取る"""
        while True:
            event = pygame.event.poll()
            if event.type == KEYDOWN:
                return event.key
            else:
                pass

    def draw(self, screen, message):
        """ウィンドウ表示"""
        Window.draw(self, screen)
        if len(message) != 0:
            self.msg_engine.draw_string(screen, self.inner_rect, message)
            pygame.display.flip()

    def ask(self, screen, question):
        """質問と答えを表示"""
        cur_str = []
        self.show()
        self.draw(screen, question)
        num = 0
        while True:
            key = self.get_key()
            if key == K_BACKSPACE:
                cur_str = cur_str[0:-1]
                if num != 0:
                    num -= 1
            elif key == K_RETURN:
                break
            elif K_0 <= key <= K_9 or K_a <= key <= K_z:
                if num <= 9:
                    cur_str.append(chr(key).upper())
                    num += 1
            self.draw(screen, question + u" " + "".join(cur_str))
        return "".join(cur_str)


class Paddle_left(pygame.sprite.Sprite):
    """ボールを打つパドル"""

    def __init__(self, paddle_left_name):
        # containersはmain()でセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image(paddle_left_name)
        self.rect.bottom = SCR_RECT.bottom-200  # パドルは画面の一番下

    def update(self):
        # 矢印でパドル移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)
        self.rect.clamp_ip(SCR_RECT)  # SCR_RECT内でしか移動できなくなる


class Paddle_right(pygame.sprite.Sprite):
    """ボールを打つパドル"""

    def __init__(self, paddle_right_name):
        # containersはmain()でセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image(paddle_right_name)
        self.rect.bottom = SCR_RECT.bottom-20  # パドルは画面の一番下

    def update(self):

        # マウスクリックされた状態で、マウスでパッドル移動
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.clamp_ip(SCR_RECT)  # SCR_RECT内でしか移動できなくなる


class Ball(pygame.sprite.Sprite):
    """ボール"""
    speed = 5  # 球速
    angle_left = 135  # 最大反射角
    angle_right = 45  # 最小反射角

    def __init__(self, paddle_left, paddle_right, bricks, score):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image("ball.png")
        self.dx = self.dy = 0  # ボールの速度
        self.paddle_left = paddle_left  # パドルへの参照
        self.paddle_right = paddle_right
        self.bricks = bricks  # ブロックグループへの参照
        self.count = [0, 0]  # ブロック衝突回数(通算,1セット)
        self.through = 0  # 貫通処理のフラグ
        self.clear = 100  # 初期ブロック数
        self.levflg = 0  # レベルUP処理のフラグ
        self.life = 3  # 残機数
        self.time = 0  # 処理時間
        self.score = score
        self.update = self.start

    def start(self):
        if self.life == 3:
            self.clear = len(Brick.containers[1])
        """ボールの位置を初期化"""
        # パドルの中央に配置
        self.rect.centerx = self.paddle_left.rect.centerx
        self.rect.bottom = self.paddle_left.rect.top
        # 左クリックで移動開始
        # 上矢印での開始を追加
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or pygame.mouse.get_pressed()[0] == 1:
            self.dx = 0
            self.dy = -self.speed
            # update()をmove()に置き換え
            self.update = self.move

    def move(self):
        """ボールの移動"""
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        self.time += 1

        # 壁との反射
        if self.rect.left < SCR_RECT.left:  # 左側
            self.rect.left = SCR_RECT.left
            self.dx = -self.dx  # 速度を反転
        if self.rect.right > SCR_RECT.right:  # 右側
            self.rect.right = SCR_RECT.right
            self.dx = -self.dx
        if self.rect.top < SCR_RECT.top:  # 上側
            self.rect.top = SCR_RECT.top
            self.dy = -self.dy
        # パドルとの反射
        if self.rect.colliderect(self.paddle_left.rect) and self.dy > 0:
            self.count[1] = 0  # カウント数の初期化
            self.through = 0  # 貫通フラグの初期化
            # 残り30%の時点でレベル(スピード)UP
            if self.count[0] >= int(self.clear*0.7) \
               and self.levflg == 0:
                self.speed = 7
                self.levflg = 1
                self.levelup_sound.play()
            # パドルの左端に当たったとき135度方向、右端で45度方向とし、
            # その間は線形補間で反射方向を計算
            x1 = self.paddle_left.rect.left - self.rect.width  # ボールが当たる左端
            y1 = self.angle_left  # 左端での反射方向（135度）
            x2 = self.paddle_left.rect.right  # ボールが当たる右端
            y2 = self.angle_right  # 右端での反射方向（45度）
            m = float(y2 - y1) / (x2 - x1)  # 直線の傾き
            x = self.rect.left  # ボールが当たった位置
            y = m * (x - x1) + y1
            angle = math.radians(y)
            self.dx = self.speed * math.cos(angle)  # float
            self.dy = -self.speed * math.sin(angle)  # float
           
            self.paddle_sound.play()

        if self.rect.colliderect(self.paddle_right.rect) and self.dy > 0:
            self.count[1] = 0  # カウント数の初期化
            self.through = 0  # 貫通フラグの初期化
            # 残り30%の時点でレベル(スピード)UP
            if self.count[0] >= int(self.clear*0.7) \
               and self.levflg == 0:
                self.speed = 7
                self.levflg = 1
                self.levelup_sound.play()
            # パドルの左端に当たったとき135度方向、右端で45度方向とし、
            # その間は線形補間で反射方向を計算
            # ボールが当たる左端
            x1 = self.paddle_right.rect.left - self.rect.width
            y1 = self.angle_left  # 左端での反射方向（135度）
            x2 = self.paddle_right.rect.right  # ボールが当たる右端
            y2 = self.angle_right  # 右端での反射方向（45度）
            m = float(y2 - y1) / (x2 - x1)  # 直線の傾き
            x = self.rect.left  # ボールが当たった位置
            y = m * (x - x1) + y1
            angle = math.radians(y)
            self.dx = self.speed * math.cos(angle)  # float
            self.dy = -self.speed * math.sin(angle)  # float
            self.paddle_sound.play()

        # ボールを落とした場合
        if self.rect.top > SCR_RECT.bottom:
            self.count[1] = 0  # カウント数の初期化
            self.through = 0  # 貫通フラグの初期化
            self.update = self.start  # ボールを初期状態に
            self.fall_sound.play()
            self.score.add_score(DEDUCTION)
            self.life -= 1
        # ブロックを壊す
        # ボールと衝突したブロックリストを取得

        bricks_collided = pygame.sprite.spritecollide(self, self.bricks, True)
        if bricks_collided:  # 衝突ブロックがある場合
            oldrect = self.rect
            if len(bricks_collided) == 2 or self.through == 1:
                self.through = 1  # 2つ同時破壊で貫通フラグON
                self.count[0] += len(bricks_collided)  # カウント数加算
                self.count[1] += len(bricks_collided)
                self.score.add_score(RATE*self.count[1]*len(bricks_collided))
                self.through_sound.play()

            else:  # 貫通フラグOFF時の反射処理
                for brick in bricks_collided:  # 各衝突ブロックに対して
                    # ボールが左から衝突
                    if oldrect.left < brick.rect.left < \
                       oldrect.right < brick.rect.right:
                        self.rect.right = brick.rect.left
                        self.dx = -self.dx
                    # ボールが右から衝突
                    if brick.rect.left < oldrect.left < \
                       brick.rect.right < oldrect.right:
                        self.rect.left = brick.rect.right
                        self.dx = -self.dx
                    # ボールが上から衝突
                    if oldrect.top < brick.rect.top < \
                       oldrect.bottom < brick.rect.bottom:
                        self.rect.bottom = brick.rect.top
                        self.dy = -self.dy
                    # ボールが下から衝突
                    if brick.rect.top < oldrect.top < \
                       brick.rect.bottom < oldrect.bottom:
                        self.rect.top = brick.rect.bottom
                        self.dy = -self.dy
                    self.brick_sound.play()
                    self.count[0] += 1  # カウント数加算処理
                    self.count[1] += 1
                    self.score.add_score(RATE*self.count[1])

        if len(self.bricks) == 0:  # クリア時処理
            if self.time <= FRAME*BONUSTIME:  # 3分以内でスコアボーナス
                check = self.score.add_score(FRAME*BONUSTIME-self.time)


class Score():
    def __init__(self):
        self.score = INIT_SCORE

    def add_score(self, x):
        self.score += x
        return self.score


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        # 列ごとにブロックの色を変更
        if y == 1:
            self.image, self.rect = load_image("brick_p.png")
        elif y == 2:
            self.image, self.rect = load_image("brick_r.png")
        elif y == 3:
            self.image, self.rect = load_image("brick_o.png")
        elif y == 4:
            self.image, self.rect = load_image("brick_y.png")
        elif y == 5:
            self.image, self.rect = load_image("brick_lg.png")
        elif y == 6:
            self.image, self.rect = load_image("brick_g.png")
        elif y == 7:
            self.image, self.rect = load_image("brick_lb.png")
        elif y == 8:
            self.image, self.rect = load_image("brick_b.png")
        elif y == 9:
            self.image, self.rect = load_image("brick_v.png")
        else:
            self.image, self.rect = load_image("brick.png")
        # ブロックの位置を更新
        self.rect.left = SCR_RECT.left + x * self.rect.width
        self.rect.top = SCR_RECT.top + y * self.rect.height


def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    filename = os.path.join("data", filename)
    # try:
    #    image = pygame.image.load(filename)
    # except pygame.error, message:
    image = pygame.image.load(filename)
    #    print "Cannot load image:", filename
    #    raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(filename):
    filename = os.path.join("data", filename)
    return pygame.mixer.Sound(filename)


def Ranking(N, S, mode):
    """ランキング計算"""
    list = []
    try:
        fout = open('ranking.txt', 'r')
        lines = fout.readlines()
        fout.close()
    except:
        lines = ""
    # 一行ずつリストに代入
    for line in lines:
        line = line.strip()
        name, score = line.split(',')
        list.append((name, int(score)))

    if mode == 0:
        # 検索用に名前にタグをつける
        NN = "#" + N
        list.append((NN, S))

    # スコアで降順ソート
    if len(list) != 0:
        list.sort(key=itemgetter(1), reverse=True)
        Len = len(list)
        if mode == 0:
            Rank = list.index((NN, S)) + 1
        else:
            Rank = 0

    else:
        Len = 0
        Rank = 0
    return list, Len, Rank


def Rank_Write(N, S):
    """結果をファイルに書き込み"""
    fout = open('ranking.txt', 'a')
    fout.write(N+','+str(S)+'\n')
    fout.close()


def Rank_Draw(screen, list, height, start, n):
    """上位ランカーを画面に描画"""
    font = pygame.font.Font(None, 25)
    if len(list) != 0:
        for i in range(start, start+n):
            # start から n 人の順位を表示する
            if i >= len(list):
                break

            # 今回のスコアがあればハイライト表示
            if list[i][0].find('#') == 0:
                ranker_num = font.render(str(i+1), True, (255, 255, 0))
                name = list[i][0].strip('#')
                ranker_name = font.render(name, True, (255, 255, 0))
                ranker_score = font.render(str(list[i][1]),
                                           True, (255, 255, 0))
            else:
                ranker_num = font.render(str(i+1), True, (255, 255, 255))
                ranker_name = font.render(list[i][0], True, (255, 255, 255))
                ranker_score = font.render(str(list[i][1]), True,
                                           (255, 255, 255))

            screen.blit(ranker_num,
                        (70-ranker_num.get_width(), height+25*(i-start+1)))
            screen.blit(ranker_name, (80, height+25*(i-start+1)))
            screen.blit(ranker_score,
                        (300-ranker_score.get_width(), height+25*(i-start+1)))

    else:
        message = font.render("Nobody has played yet",
                              True, (255, 255, 255))
        screen.blit(message, ((H-message.get_width())/2, height+50))

if __name__ == "__main__":
    MyScreen()
