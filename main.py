#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面宠物 - 安卓版
基于Kivy框架开发
"""

import os
import random
import math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

# 尝试导入Android相关模块
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    HAS_ANDROID = True
except ImportError:
    HAS_ANDROID = False

# ============== 配置区 ==============
CHARACTER_FILES = ["character.png", "character2.png"]
CHARACTER_NAMES = ["真人版", "卡通版"]
HUG_FILE = "hug.png"
DEFAULT_SIZE = dp(120)
BUBBLE_DURATION = 3
HUG_INTERVAL = 45

# 对话内容
DIALOGUES = [
    "嘿嘿，你戳我干嘛呀~", "好开心呀！", "今天也要加油哦！",
    "摸摸头~", "我在呢！", "嘻嘻，被你发现啦", "想吃好吃的！",
    "陪我玩嘛~", "你好呀！", "困困...想睡觉", "走路走路！",
    "抱抱！", "我超可爱的对吧？", "别挠我痒痒！", "一起玩吧~",
]

PET_DIALOGUES = ["好舒服~", "再摸摸嘛~", "嘿嘿~", "喜欢被摸头！", "幸福~"]
EAT_DIALOGUES = ["好吃！", "吧唧吧唧~", "还要还要！", "谢谢投喂~", "吃饱啦！"]
SLEEP_DIALOGUES = ["呼...呼...", "好困呀...", "晚安~", "做个好梦...", "zzz..."]
WALK_DIALOGUES = ["走路走路~", "我去散步啦！", "一二一~", "散步真开心~"]
HUG_DIALOGUES = [
    "抱抱好舒服~", "谢谢你的抱抱！", "好温暖呀~", "再抱一下嘛~",
    "最喜欢你了！", "抱抱真开心！", "嘿嘿，被抱住啦~", "还要还要！",
]
CHAT_DIALOGUES = [
    "今天过得怎么样呀？", "有什么开心的事吗？", "我一直陪着你哦~",
    "工作辛苦了！", "要不要休息一下？", "你今天真好看！",
    "加油加油，你最棒了！", "有什么烦恼可以跟我说~",
]


class BubbleWidget(Widget):
    """对话气泡"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = ""
        self.size_hint = (None, None)
        self.opacity = 0
        with self.canvas:
            self.bg_color = Color(1, 1, 1, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12,])
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def show_text(self, text, duration=BUBBLE_DURATION):
        self.text = text
        from kivy.core.text import Label as CoreLabel
        label = CoreLabel(text=text, font_size=dp(14), font_name="Roboto")
        label.refresh()
        text_size = label.texture.size
        w = min(text_size[0] + dp(30), dp(200))
        h = text_size[1] + dp(25)
        self.size = (w, h)
        self.opacity = 1
        Clock.schedule_once(lambda dt: self._hide(), duration)
    
    def _hide(self):
        self.opacity = 0
    
    def on_touch_down(self, touch):
        return False


class PetImage(Image):
    """宠物图片控件"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.allow_stretch = True
        self.keep_ratio = True
        self.is_dragging = False
        self.drag_start = (0, 0)
        self.original_pos = (0, 0)
        self.base_size = DEFAULT_SIZE
        self.size = (self.base_size, self.base_size)


class DesktopPetApp(App):
    """桌面宠物主应用"""
    
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.1, 1)
        
        self.root = FloatLayout()
        
        self.current_character = 0
        self.character_textures = []
        self.hug_texture = None
        self.is_hugging = False
        self.normal_texture = None
        self.is_sleeping = False
        self.is_walking = False
        self.walk_direction = 1
        self.walk_speed = dp(3)
        self.anim_timer = None
        self.walk_timer = None
        
        self._load_images()
        
        self.pet = PetImage()
        if self.character_textures:
            self.pet.texture = self.character_textures[0]
        self.pet.pos = (Window.width // 2 - DEFAULT_SIZE // 2, 
                        Window.height // 2 - DEFAULT_SIZE // 2)
        self.root.add_widget(self.pet)
        
        self.bubble = BubbleWidget()
        self.root.add_widget(self.bubble)
        
        self._create_control_bar()
        
        self.random_bubble_timer = Clock.schedule_interval(
            lambda dt: self._random_bubble(), 15)
        self.hug_timer = Clock.schedule_interval(
            lambda dt: self._auto_hug(), HUG_INTERVAL)
        
        Window.bind(on_touch_down=self._on_window_touch)
        
        return self.root
    
    def _load_images(self):
        for fname in CHARACTER_FILES:
            path = self._get_resource_path(fname)
            if os.path.exists(path):
                try:
                    tex = CoreImage(path).texture
                    self.character_textures.append(tex)
                except:
                    pass
        
        hug_path = self._get_resource_path(HUG_FILE)
        if os.path.exists(hug_path):
            try:
                self.hug_texture = CoreImage(hug_path).texture
            except:
                pass
    
    def _get_resource_path(self, filename):
        if hasattr(self, 'user_data_dir'):
            return os.path.join(self.user_data_dir, filename)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    def _create_control_bar(self):
        bar = BoxLayout(
            size_hint=(1, None),
            height=dp(55),
            pos_hint={'bottom': 0},
            spacing=dp(5),
            padding=dp(10),
        )
        
        buttons = [
            ("💬", "聊天", self.chat),
            ("🤚", "摸头", self.pet_head),
            ("🍖", "喂食", self.feed),
            ("🔄", "切换", self.switch_character),
            ("🚶", "走路", self.toggle_walk),
            ("😴", "睡觉", self.toggle_sleep),
        ]
        
        for emoji, name, callback in buttons:
            btn = Button(
                text=emoji,
                font_size=dp(22),
                size_hint=(1, 1),
                background_normal='',
                background_color=(0.3, 0.3, 0.4, 0.8),
            )
            btn.bind(on_press=lambda x, cb=callback: cb())
            bar.add_widget(btn)
        
        self.root.add_widget(bar)
    
    def _on_window_touch(self, instance, touch):
        if self.pet.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                return False
            if 'button' in touch.profile and touch.button == 'right':
                return False
            if touch.op == 'down':
                self.pet.is_dragging = True
                self.pet.drag_start = (touch.x, touch.y)
                self.pet.original_pos = self.pet.pos
                touch.grab(self.pet)
                return True
        return False
    
    def on_touch_move(self, touch):
        if touch.grab_current is self.pet and self.pet.is_dragging:
            dx = touch.x - self.pet.drag_start[0]
            dy = touch.y - self.pet.drag_start[1]
            new_x = self.pet.original_pos[0] + dx
            new_y = self.pet.original_pos[1] + dy
            new_x = max(0, min(new_x, Window.width - self.pet.width))
            new_y = max(dp(70), min(new_y, Window.height - self.pet.height - dp(70)))
            self.pet.pos = (new_x, new_y)
            self._update_bubble_position()
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self.pet:
            touch.ungrab(self.pet)
            self.pet.is_dragging = False
            dx = abs(touch.x - self.pet.drag_start[0])
            dy = abs(touch.y - self.pet.drag_start[1])
            if dx < dp(15) and dy < dp(15):
                if self.is_hugging:
                    self.stop_hug()
                else:
                    self._trigger_interaction()
            return True
        return super().on_touch_up(touch)
    
    def _trigger_interaction(self):
        animations = ['jump', 'squash', 'shake']
        anim = random.choice(animations)
        self._play_animation(anim)
        self._show_bubble(random.choice(DIALOGUES))
    
    def _play_animation(self, anim_type):
        if self.anim_timer:
            self.anim_timer.cancel()
        
        self.anim_frame = 0
        self.anim_type = anim_type
        
        def anim_step(dt):
            self.anim_frame += 1
            frame = self.anim_frame
            
            if anim_type == 'jump':
                if frame <= 10:
                    self.pet.scale = 1.0 + frame * 0.02
                elif frame <= 20:
                    self.pet.scale = 1.2 - (frame - 10) * 0.02
                else:
                    self.pet.scale = 1.0
                    self.anim_timer.cancel()
                    return
            elif anim_type == 'squash':
                if frame <= 10:
                    self.pet.scale = 1.0 - frame * 0.015
                elif frame <= 20:
                    self.pet.scale = 0.85 + (frame - 10) * 0.015
                else:
                    self.pet.scale = 1.0
                    self.anim_timer.cancel()
                    return
            elif anim_type == 'shake':
                if frame <= 15:
                    self.pet.rotation = math.sin(frame * 0.8) * 5
                else:
                    self.pet.rotation = 0
                    self.anim_timer.cancel()
                    return
        
        self.anim_timer = Clock.schedule_interval(anim_step, 0.03)
    
    def _show_bubble(self, text, duration=BUBBLE_DURATION):
        self.bubble.show_text(text, duration)
        Clock.schedule_once(lambda dt: self._update_bubble_position(), 0.05)
    
    def _update_bubble_position(self):
        if self.bubble.opacity > 0:
            x = self.pet.center_x - self.bubble.width / 2
            y = self.pet.top + dp(5)
            self.bubble.pos = (x, y)
    
    def _random_bubble(self):
        if not self.is_sleeping and not self.is_hugging:
            if random.random() < 0.5:
                self._show_bubble(random.choice(DIALOGUES))
    
    def chat(self):
        if self.is_sleeping:
            self.stop_sleeping()
        self._show_bubble(random.choice(CHAT_DIALOGUES), 4)
    
    def pet_head(self):
        if self.is_sleeping:
            self.stop_sleeping()
        if self.current_character == 1 and self.hug_texture is not None:
            self.start_hug()
            return
        self._play_animation('squash')
        self._show_bubble(random.choice(PET_DIALOGUES))
    
    def feed(self):
        if self.is_sleeping:
            self.stop_sleeping()
        self._play_animation('squash')
        self._show_bubble(random.choice(EAT_DIALOGUES))
    
    def switch_character(self):
        if self.is_hugging:
            self.stop_hug()
        if len(self.character_textures) <= 1:
            self._show_bubble("只有一个角色哦~")
            return
        self.current_character = (self.current_character + 1) % len(self.character_textures)
        self.pet.texture = self.character_textures[self.current_character]
        name = CHARACTER_NAMES[self.current_character] if self.current_character < len(CHARACTER_NAMES) else f"角色{self.current_character+1}"
        self._show_bubble(f"切换到{name}！")
    
    def toggle_walk(self):
        if self.is_walking:
            self.stop_walking()
        else:
            self.start_walking()
    
    def start_walking(self):
        if self.is_sleeping:
            self.stop_sleeping()
        self.is_walking = True
        self._show_bubble(random.choice(WALK_DIALOGUES))
        
        def walk_step(dt):
            if not self.is_walking:
                return
            x = self.pet.x + self.walk_direction * self.walk_speed
            if x <= 0 or x >= Window.width - self.pet.width:
                self.walk_direction *= -1
                x = max(0, min(x, Window.width - self.pet.width))
            self.pet.x = x
            self._update_bubble_position()
        
        self.walk_timer = Clock.schedule_interval(walk_step, 0.05)
    
    def stop_walking(self):
        self.is_walking = False
        if self.walk_timer:
            self.walk_timer.cancel()
            self.walk_timer = None
    
    def toggle_sleep(self):
        if self.is_sleeping:
            self.stop_sleeping()
        else:
            self.start_sleeping()
    
    def start_sleeping(self):
        self.stop_walking()
        self.is_sleeping = True
        self._show_bubble(random.choice(SLEEP_DIALOGUES))
    
    def stop_sleeping(self):
        self.is_sleeping = False
    
    def start_hug(self):
        if self.is_hugging or self.hug_texture is None:
            return
        if self.current_character != 1:
            return
        self.is_hugging = True
        self.normal_texture = self.pet.texture
        self.pet.texture = self.hug_texture
        self._show_bubble("抱抱我~", 5)
    
    def stop_hug(self):
        if not self.is_hugging:
            return
        self.is_hugging = False
        if self.normal_texture:
            self.pet.texture = self.normal_texture
            self.normal_texture = None
        self._show_bubble(random.choice(HUG_DIALOGUES), 3)
    
    def _auto_hug(self):
        if self.is_sleeping or self.is_walking or self.is_hugging:
            return
        if self.current_character != 1:
            return
        if random.random() < 0.6:
            self.start_hug()


if __name__ == "__main__":
    DesktopPetApp().run()
