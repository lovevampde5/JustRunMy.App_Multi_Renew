#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import requests
from seleniumbase import SB

# 修正后的配置
LOGIN_URL = "https://justrunmy.app/id/Account/Login"

# ============================================================
#  环境变量对接 (由 .yml 传入)
# ============================================================
EMAIL        = os.environ.get("JUSTRUNMY_EMAIL")
PASSWORD     = os.environ.get("JUSTRUNMY_PASSWORD")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID   = os.environ.get("TG_CHAT_ID")

if not EMAIL or not PASSWORD:
    print("❌ 致命错误：未找到 JUSTRUNMY_EMAIL 或 JUSTRUNMY_PASSWORD！")
    sys.exit(1)

def send_tg_message(status_icon, status_text, time_left):
    if not TG_BOT_TOKEN or not TG_CHAT_ID: return
    local_time = time.gmtime(time.time() + 8 * 3600)
    current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    message = (
        f"{status_icon} *JustRunMy 自动续期*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📧 *账号*: `{EMAIL[:3]}***`\n"
        f"📝 *状态*: {status_text}\n"
        f"⏱️ *剩余*: {time_left}\n"
        f"📅 *时间*: {current_time_str}\n"
        f"━━━━━━━━━━━━━━━"
    )
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", json=payload, timeout=10)
    except: pass

def main():
    print(f"🚀 开始执行续期任务: {EMAIL[:3]}***")
    
    with SB(uc=True, test=True, headless=False) as sb:
        try:
            # 1. 打开登录页
            sb.uc_open_with_reconnect(LOGIN_URL, reconnect_time=5)
            sb.sleep(5)

            # 2. 填写表单 (修正选择器: 去掉 Input. 前缀)
            print("📧 正在填写登录信息...")
            sb.wait_for_element('input[name="Email"]', timeout=15)
            sb.type('input[name="Email"]', EMAIL)
            sb.type('input[name="Password"]', PASSWORD)
            
            # 3. 处理可能存在的 Cookie 弹窗
            try:
                if sb.is_element_visible('button:contains("Accept")'):
                    sb.click('button:contains("Accept")')
            except: pass

            # 4. 点击登录
            print("🖱️ 点击登录按钮...")
            sb.click('button[type="submit"]')
            sb.sleep(10)

            # 5. 检查是否进入面板
            if "Login" in sb.get_current_url():
                print("❌ 登录未跳转，尝试处理可能的人机验证...")
                sb.save_screenshot("login_stuck.png")
                # 如果依然在登录页，可能是被 CF 挡住了，尝试回车
                sb.press_keys('input[name="Password"]', '\n')
                sb.sleep(8)

            # 6. 续期逻辑
            print("🌐 进入控制面板...")
            sb.open("https://justrunmy.app/panel")
            sb.sleep(5)
            
            # 查找并进入应用 (参考原版逻辑)
            sb.wait_for_element('h3.font-semibold', timeout=10)
            app_name = sb.get_text('h3.font-semibold')
            sb.click('h3.font-semibold')
            sb.sleep(3)

            print(f"🎯 正在为 [{app_name}] 执行续期...")
            sb.click('button:contains("Reset Timer")')
            sb.sleep(3)
            sb.click('button:contains("Just Reset")')
            sb.sleep(5)

            # 7. 结果验证
            sb.refresh()
            sb.sleep(3)
            timer_text = sb.get_text('span.font-mono.text-xl')
            print(f"✅ 续期成功！剩余时间: {timer_text}")
            sb.save_screenshot("renew_success.png")
            send_tg_message("✅", "续期成功", timer_text)

        except Exception as e:
            print(f"💥 运行异常: {e}")
            sb.save_screenshot("error.png")
            send_tg_message("❌", "运行出错", "请检查 Action 截图")

if __name__ == "__main__":
    main()
