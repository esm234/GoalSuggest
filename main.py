#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تليجرام لاستقبال اقتراحات المستخدمين وإرسالها لمجموعة الإدارة
Telegram Bot for receiving user suggestions and sending them to admin group
"""

import os
import logging
from bot import SuggestionBot

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
    
    try:
        admin_group_id = int(admin_group_id)
    except ValueError:
        logger.error("❌ ADMIN_GROUP_ID يجب أن يكون رقماً صحيحاً")
        return
    
    logger.info("🚀 بدء تشغيل البوت...")
    
    # إنشاء وتشغيل البوت
    bot = SuggestionBot(bot_token, admin_group_id)
    bot.run()

if __name__ == '__main__':
    main()
