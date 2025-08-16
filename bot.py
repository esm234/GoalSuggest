#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فئة البوت الرئيسية لمعالجة الاقتراحات
Main Bot class for handling suggestions
"""

import logging
import html
import os
import asyncio
from telegram._update import Update
from telegram._bot import Bot
from telegram._message import Message

class SuggestionBot:
    def __init__(self, bot_token: str, admin_group_id: int):
        """
        تهيئة البوت
        
        Args:
            bot_token (str): رمز البوت من BotFather
            admin_group_id (int): معرف مجموعة الإدارة
        """
        self.bot_token = bot_token
        self.admin_group_id = admin_group_id
        self.logger = logging.getLogger(__name__)
        self.bot = Bot(token=bot_token)
        self.running = True
    
    async def _start_command(self, update: Update):
        """
        معالج أمر /start
        Handler for /start command
        """
        welcome_message = (
            "👋 أهلاً بيك!\n\n"
            "ابعتلي أي ميزة حابب تضيفها لموقع Our Goal\n\n"
            "سيتم إرسال اقتراحك مباشرة للمسؤولين 📩"
        )
        
        try:
            await self.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_message,
                parse_mode='HTML'
            )
            
            # تسجيل استخدام أمر البداية
            user = update.effective_user
            self.logger.info(
                f"مستخدم جديد بدأ البوت: {user.full_name} (@{user.username}) - ID: {user.id}"
            )
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة أمر /start: {e}")
    
    async def _handle_suggestion(self, update: Update):
        """
        معالج الاقتراحات من المستخدمين
        Handler for user suggestions
        """
        user = update.effective_user
        message = update.message
        
        try:
            # إنشاء رسالة الاقتراح للإدارة
            suggestion_text = html.escape(message.text)
            user_info = self._format_user_info(user)
            
            admin_message = (
                "📩 <b>اقتراح جديد</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💭 <b>الاقتراح:</b>\n{suggestion_text}\n\n"
                f"👤 <b>معلومات المستخدم:</b>\n{user_info}\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            
            # إرسال الاقتراح لمجموعة الإدارة
            await self.bot.send_message(
                chat_id=self.admin_group_id,
                text=admin_message,
                parse_mode='HTML'
            )
            
            # رد الشكر للمستخدم
            thank_you_message = "✅ تم إرسال اقتراحك للمسؤولين، شكراً لك!"
            await self.bot.send_message(
                chat_id=update.effective_chat.id,
                text=thank_you_message
            )
            
            # تسجيل العملية
            self.logger.info(
                f"تم إرسال اقتراح من {user.full_name} (@{user.username}) - ID: {user.id}"
            )
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الاقتراح: {e}")
            
            # إرسال رسالة خطأ للمستخدم
            error_message = (
                "❌ عذراً، حدث خطأ أثناء إرسال اقتراحك.\n"
                "يرجى المحاولة مرة أخرى لاحقاً."
            )
            
            try:
                await self.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message
                )
            except:
                pass  # في حالة فشل إرسال رسالة الخطأ أيضاً
    
    def _format_user_info(self, user) -> str:
        """
        تنسيق معلومات المستخدم
        Format user information
        
        Args:
            user: كائن المستخدم من تليجرام
            
        Returns:
            str: معلومات المستخدم منسقة
        """
        user_info_parts = []
        
        # الاسم
        if user.full_name:
            user_info_parts.append(f"الاسم: {html.escape(user.full_name)}")
        
        # اسم المستخدم
        if user.username:
            user_info_parts.append(f"المعرف: @{user.username}")
        
        # معرف المستخدم
        user_info_parts.append(f"ID: <code>{user.id}</code>")
        
        # رابط الملف الشخصي
        user_info_parts.append(f"الرابط: <a href='tg://user?id={user.id}'>الملف الشخصي</a>")
        
        return "\n".join(user_info_parts)
    
    async def process_update(self, update: Update):
        """معالج التحديثات الرئيسي"""
        try:
            # تجاهل الرسائل من المجموعات (فقط الرسائل الخاصة)
            if update.effective_chat.type != 'private':
                return
            
            # معالجة أمر /start
            if update.message and update.message.text and update.message.text.startswith('/start'):
                await self._start_command(update)
            # معالجة النصوص العادية
            elif update.message and update.message.text and not update.message.text.startswith('/'):
                await self._handle_suggestion(update)
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة التحديث: {e}")
    
    async def get_updates(self):
        """الحصول على التحديثات من تليجرام"""
        offset = 0
        while self.running:
            try:
                updates = await self.bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=["message"]
                )
                
                for update in updates:
                    await self.process_update(update)
                    offset = update.update_id + 1
                    
            except Exception as e:
                self.logger.error(f"خطأ في الحصول على التحديثات: {e}")
                await asyncio.sleep(5)
    
    def run(self):
        """تشغيل البوت"""
        try:
            self.logger.info("✅ البوت جاهز للعمل!")
            asyncio.run(self.get_updates())
        except KeyboardInterrupt:
            self.logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
            self.running = False
        except Exception as e:
            self.logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        finally:
            self.logger.info("👋 تم إغلاق البوت")