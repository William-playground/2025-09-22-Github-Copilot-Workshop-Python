#!/usr/bin/env python3
"""
ポモドーロタイマーのデモスクリプト
Demo script for Pomodoro Timer with accelerated timing for demonstration
"""

import tkinter as tk
from tkinter import ttk
import math
import time
import threading
from typing import Tuple, List
import random


class DemoPomodoroTimer:
    """デモ用のポモドーロタイマー（加速版）"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ポモドーロタイマー - デモ版（加速）")
        self.root.geometry("600x700")
        self.root.configure(bg="#1a1a2e")
        
        # タイマー設定（デモ用に短縮）
        self.work_duration = 30  # 30秒（通常25分）
        self.break_duration = 10  # 10秒（通常5分）
        self.current_duration = self.work_duration
        self.remaining_time = self.work_duration
        self.is_running = False
        self.is_work_session = True
        
        # UI要素
        self.canvas = None
        self.particles: List = []
        self.last_update_time = time.time()
        
        # アニメーション設定
        self.center_x = 300
        self.center_y = 250
        self.radius = 150
        
        self.setup_ui()
        self.start_animation_loop()
    
    def setup_ui(self):
        """UIセットアップ"""
        # メインフレーム
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(
            main_frame, 
            text="ポモドーロタイマー（デモ版）",
            font=("Helvetica", 24, "bold"),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        title_label.pack(pady=(0, 10))
        
        # デモ説明
        demo_label = tk.Label(
            main_frame, 
            text="デモ用加速版: 作業30秒、休憩10秒",
            font=("Helvetica", 12),
            fg="#cccccc",
            bg="#1a1a2e"
        )
        demo_label.pack(pady=(0, 20))
        
        # キャンバス（メイン表示エリア）
        self.canvas = tk.Canvas(
            main_frame,
            width=600,
            height=400,
            bg="#0f0f1e",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # 時間表示
        self.time_label = tk.Label(
            main_frame,
            text=self.format_time(self.remaining_time),
            font=("Helvetica", 36, "bold"),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        self.time_label.pack(pady=10)
        
        # セッション表示
        self.session_label = tk.Label(
            main_frame,
            text="作業セッション",
            font=("Helvetica", 16),
            fg="#4a9eff",
            bg="#1a1a2e"
        )
        self.session_label.pack(pady=5)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg="#1a1a2e")
        button_frame.pack(pady=20)
        
        # ボタンスタイル
        button_style = {
            "font": ("Helvetica", 14, "bold"),
            "width": 10,
            "height": 2,
            "relief": "flat",
            "cursor": "hand2"
        }
        
        self.start_button = tk.Button(
            button_frame,
            text="開始",
            bg="#4a9eff",
            fg="white",
            command=self.toggle_timer,
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(
            button_frame,
            text="リセット",
            bg="#ff6b6b",
            fg="white",
            command=self.reset_timer,
            **button_style
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
    
    def format_time(self, seconds: int) -> str:
        """秒を MM:SS 形式にフォーマット"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_color(self, progress: float) -> str:
        """進行状況に基づいて色を計算（青→黄→赤）"""
        if progress < 0.33:
            # 青から黄色へ (0.0 - 0.33)
            ratio = progress / 0.33
            r = int(74 + (255 - 74) * ratio)
            g = int(158 + (255 - 158) * ratio)
            b = int(255 + (0 - 255) * ratio)
        elif progress < 0.66:
            # 黄色から赤へ (0.33 - 0.66)
            ratio = (progress - 0.33) / 0.33
            r = 255
            g = int(255 + (107 - 255) * ratio)
            b = 0
        else:
            # 赤の維持 (0.66 - 1.0)
            r, g, b = 255, 107, 107
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def draw_progress_circle(self):
        """円形プログレスバーを描画"""
        self.canvas.delete("progress")
        
        # 進行状況計算
        progress = 1.0 - (self.remaining_time / self.current_duration)
        angle = 2 * math.pi * progress
        
        # 背景円
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="#2a2a4e",
            width=8,
            tags="progress"
        )
        
        # プログレス円弧
        if progress > 0:
            color = self.get_progress_color(progress)
            
            # 円弧を複数のセグメントで描画（滑らかなアニメーション）
            segments = max(1, int(angle * 50))  # 細かいセグメント
            for i in range(segments):
                start_angle = (i * angle / segments) - math.pi/2
                end_angle = ((i + 1) * angle / segments) - math.pi/2
                
                x1 = self.center_x + (self.radius - 4) * math.cos(start_angle)
                y1 = self.center_y + (self.radius - 4) * math.sin(start_angle)
                x2 = self.center_x + (self.radius + 4) * math.cos(start_angle)
                y2 = self.center_y + (self.radius + 4) * math.sin(start_angle)
                x3 = self.center_x + (self.radius + 4) * math.cos(end_angle)
                y3 = self.center_y + (self.radius + 4) * math.sin(end_angle)
                x4 = self.center_x + (self.radius - 4) * math.cos(end_angle)
                y4 = self.center_y + (self.radius - 4) * math.sin(end_angle)
                
                self.canvas.create_polygon(
                    x1, y1, x2, y2, x3, y3, x4, y4,
                    fill=color,
                    outline="",
                    tags="progress"
                )
        
        # 中央の円
        inner_radius = self.radius - 30
        self.canvas.create_oval(
            self.center_x - inner_radius,
            self.center_y - inner_radius,
            self.center_x + inner_radius,
            self.center_y + inner_radius,
            fill="#1a1a2e",
            outline="",
            tags="progress"
        )
    
    def spawn_particles(self):
        """パーティクルエフェクトの生成"""
        if len(self.particles) < 50:  # 最大パーティクル数制限
            for _ in range(3):  # デモ用に多めに生成
                # ランダムな位置と速度
                x = random.uniform(50, 550)
                y = random.uniform(350, 400)
                vx = random.uniform(-30, 30)
                vy = random.uniform(-50, -20)
                
                # 進行状況に基づく色
                progress = 1.0 - (self.remaining_time / self.current_duration)
                color = self.get_progress_color(progress)
                
                size = random.uniform(2, 6)
                lifetime = random.uniform(2, 4)
                
                particle = {
                    'x': x, 'y': y, 'vx': vx, 'vy': vy,
                    'color': color, 'size': size,
                    'lifetime': lifetime, 'max_lifetime': lifetime,
                    'alpha': 1.0
                }
                self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """パーティクルの更新"""
        self.canvas.delete("particle")
        
        # パーティクル更新
        alive_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['lifetime'] -= dt
            particle['alpha'] = max(0, particle['lifetime'] / particle['max_lifetime'])
            
            if particle['lifetime'] > 0:
                alive_particles.append(particle)
                
                # パーティクル描画
                alpha_color = self.blend_alpha(particle['color'], particle['alpha'])
                self.canvas.create_oval(
                    particle['x'] - particle['size']/2,
                    particle['y'] - particle['size']/2,
                    particle['x'] + particle['size']/2,
                    particle['y'] + particle['size']/2,
                    fill=alpha_color,
                    outline="",
                    tags="particle"
                )
        
        self.particles = alive_particles
    
    def blend_alpha(self, color: str, alpha: float) -> str:
        """色にアルファ値を適用"""
        # 簡易的なアルファブレンド
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # 背景色 #0f0f1e とブレンド
        bg_r, bg_g, bg_b = 15, 15, 30
        
        r = int(bg_r + (r - bg_r) * alpha)
        g = int(bg_g + (g - bg_g) * alpha)
        b = int(bg_b + (b - bg_b) * alpha)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def draw_ripple_effect(self):
        """波紋エフェクトの描画"""
        if self.is_running:
            current_time = time.time()
            ripple_phase = (current_time * 2) % (2 * math.pi)
            
            for i in range(3):
                phase_offset = i * math.pi / 3
                ripple_radius = self.radius + 20 + 15 * math.sin(ripple_phase + phase_offset)
                alpha = 0.3 + 0.2 * math.sin(ripple_phase + phase_offset)
                
                progress = 1.0 - (self.remaining_time / self.current_duration)
                base_color = self.get_progress_color(progress)
                ripple_color = self.blend_alpha(base_color, alpha)
                
                self.canvas.create_oval(
                    self.center_x - ripple_radius,
                    self.center_y - ripple_radius,
                    self.center_x + ripple_radius,
                    self.center_y + ripple_radius,
                    outline=ripple_color,
                    width=2,
                    tags="ripple"
                )
    
    def update_display(self):
        """表示の更新"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 背景エフェクトクリア
        self.canvas.delete("ripple")
        
        # 波紋エフェクト描画
        self.draw_ripple_effect()
        
        # パーティクル更新
        if self.is_running:
            self.spawn_particles()
        self.update_particles(dt)
        
        # プログレスバー描画
        self.draw_progress_circle()
        
        # 時間表示更新
        self.time_label.config(text=self.format_time(self.remaining_time))
        
        # セッション表示更新
        if self.is_work_session:
            self.session_label.config(text="作業セッション", fg="#4a9eff")
        else:
            self.session_label.config(text="休憩時間", fg="#4ecdc4")
    
    def timer_thread(self):
        """タイマースレッド"""
        while self.is_running and self.remaining_time > 0:
            time.sleep(1)
            if self.is_running:
                self.remaining_time -= 1
        
        if self.remaining_time <= 0:
            self.timer_finished()
    
    def timer_finished(self):
        """タイマー終了時の処理"""
        self.is_running = False
        self.start_button.config(text="開始")
        
        # セッション切り替え
        if self.is_work_session:
            self.is_work_session = False
            self.current_duration = self.break_duration
            self.remaining_time = self.break_duration
        else:
            self.is_work_session = True
            self.current_duration = self.work_duration
            self.remaining_time = self.work_duration
    
    def toggle_timer(self):
        """タイマーの開始/停止"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(text="開始")
        else:
            self.is_running = True
            self.start_button.config(text="停止")
            thread = threading.Thread(target=self.timer_thread, daemon=True)
            thread.start()
    
    def reset_timer(self):
        """タイマーのリセット"""
        self.is_running = False
        self.start_button.config(text="開始")
        
        if self.is_work_session:
            self.remaining_time = self.work_duration
            self.current_duration = self.work_duration
        else:
            self.remaining_time = self.break_duration
            self.current_duration = self.break_duration
        
        self.particles.clear()
    
    def start_animation_loop(self):
        """アニメーションループの開始"""
        def animate():
            self.update_display()
            self.root.after(50, animate)  # 20fps
        
        animate()
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    print("ポモドーロタイマーデモを開始します...")
    print("特徴:")
    print("- 円形プログレスバーのアニメーション")
    print("- 時間経過による色のグラデーション変化（青→黄→赤）")
    print("- 背景パーティクルアニメーション")
    print("- 波紋エフェクト")
    print("- デモ用に加速（作業30秒、休憩10秒）")
    print()
    
    app = DemoPomodoroTimer()
    app.run()