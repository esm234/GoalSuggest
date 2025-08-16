#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تليجرام بسيط لاستقبال الاقتراحات
Simple Telegram bot for receiving suggestions
"""

import os
import time
import json
import logging
import requests
from typing import Optional, Dict, Any

class SimpleTelegramBot:
    def __init__(self, token: str, admin_group_id: str):
        """
        تهيئة البوت
        Initialize the bot
        """
        self.token = token
        self.admin_group_id = admin_group_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.logger = logging.getLogger(__name__)
        
    def get_updates(self) -> list:
        """
        الحصول على التحديثات من تليجرام
        Get updates from Telegram
        """
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30,
                'allowed_updates': ['message']
            }
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
            
            return []
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على التحديثات: {e}")
            return []
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """
        إرسال رسالة
        Send a message
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200 and response.json().get('ok', False)
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الرسالة: {e}")
            return False
    
    def handle_start_command(self, chat_id: str, user_info: Dict[str, Any]) -> None:
        """
        معالج أمر /start
        Handle /start command
        """
        welcome_message = (
            "👋 أهلاً بيك!\n\n"
            "ابعتلي أي ميزة حابب تضيفها لموقع Our Goal\n\n"
            "سيتم إرسال اقتراحك مباشرة للمسؤولين 📩"
        )
        
        self.send_message(chat_id, welcome_message)
        
        # تسجيل المستخدم الجديد
        user_name = user_info.get('first_name', 'غير معروف')
        username = user_info.get('username', 'بدون معرف')
        user_id = user_info.get('id', 'غير معروف')
        
        self.logger.info(f"مستخدم جديد بدأ البوت: {user_name} (@{username}) - ID: {user_id}")
    
    def handle_suggestion(self, chat_id: str, message_text: str, user_info: Dict[str, Any]) -> None:
        """
        معالج الاقتراحات
        Handle suggestions
        """
        try:
            # معلومات المستخدم
            user_name = user_info.get('first_name', 'غير معروف')
            last_name = user_info.get('last_name', '')
            if last_name:
                user_name += f" {last_name}"
            
            username = user_info.get('username', 'بدون معرف')
            user_id = user_info.get('id', 'غير معروف')
            
            # رسالة للإدارة
            admin_message = (
                "📩 <b>اقتراح جديد</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💭 <b>الاقتراح:</b>\n{message_text}\n\n"
                f"👤 <b>معلومات المستخدم:</b>\n"
                f"الاسم: {user_name}\n"
                f"المعرف: @{username}\n"
                f"ID: <code>{user_id}</code>\n"
                f"الرابط: <a href='tg://user?id={user_id}'>الملف الشخصي</a>\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            
            # إرسال للإدارة
            if self.send_message(self.admin_group_id, admin_message):
                # رد الشكر للمستخدم
                thank_message = "✅ تم إرسال اقتراحك للمسؤولين، شكراً لك!"
                self.send_message(chat_id, thank_message)
                
                # تسجيل العملية
                self.logger.info(f"تم إرسال اقتراح من {user_name} (@{username}) - ID: {user_id}")
            else:
                # خطأ في الإرسال
                error_message = "❌ عذراً، حدث خطأ أثناء إرسال اقتراحك. يرجى المحاولة مرة أخرى."
                self.send_message(chat_id, error_message)
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الاقتراح: {e}")
            error_message = "❌ عذراً، حدث خطأ أثناء إرسال اقتراحك. يرجى المحاولة مرة أخرى."
            self.send_message(chat_id, error_message)
    
    def process_update(self, update: Dict[str, Any]) -> None:
        """
        معالجة التحديث
        Process update
        """
        try:
            message = update.get('message')
            if not message:
                return
            
            chat = message.get('chat', {})
            chat_type = chat.get('type', '')
            chat_id = str(chat.get('id', ''))
            
            # تجاهل رسائل المجموعات
            if chat_type != 'private':
                return
            
            message_text = message.get('text', '')
            user_info = message.get('from', {})
            
            # معالجة أمر /start
            if message_text.startswith('/start'):
                self.handle_start_command(chat_id, user_info)
            # معالجة الاقتراحات
            elif message_text and not message_text.startswith('/'):
                self.handle_suggestion(chat_id, message_text, user_info)
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة التحديث: {e}")
    
    def run(self) -> None:
        """
        تشغيل البوت
        Run the bot
        """
        self.logger.info("✅ البوت جاهز للعمل!")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    self.process_update(update)
                
                if not updates:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
                break
            except Exception as e:
                self.logger.error(f"❌ خطأ في تشغيل البوت: {e}")
                time.sleep(5)
        
        self.logger.info("👋 تم إغلاق البوت")


def main():
    """تشغيل البوت الرئيسي"""
    # إعداد التسجيل
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # التحقق من متغيرات البيئة
    bot_token = os.getenv("BOT_TOKEN")
    admin_group_id = os.getenv("ADMIN_GROUP_ID")
    
    if not bot_token:
        logger.error("❌ BOT_TOKEN غير موجود في متغيرات البيئة")
        return
    
    if not admin_group_id:
        logger.error("❌ ADMIN_GROUP_ID غير موجود في متغيرات البيئة")
        return
    
    logger.info("🚀 بدء تشغيل البوت...")
    
    # إنشاء وتشغيل البوت
    bot = SimpleTelegramBot(bot_token, admin_group_id)
    bot.run()


if __name__ == '__main__':
    main()