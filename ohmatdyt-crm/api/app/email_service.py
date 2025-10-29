"""
Email service для відправки нотифікацій через SMTP.

BE-014: Повна реалізація SMTP з HTML шаблонами.
Підтримує всі типи нотифікацій з красивими HTML шаблонами.
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Шлях до шаблонів
TEMPLATES_DIR = Path(__file__).parent / "templates" / "emails"

# Jinja2 Environment
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)

# SMTP Configuration з .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_SSL", "false").lower() == "true"
SMTP_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL", "noreply@ohmatdyt.com")
SMTP_FROM_NAME = os.getenv("EMAILS_FROM_NAME", "Ohmatdyt CRM")

# URL CRM для посилань у листах
CRM_URL = os.getenv("CRM_URL", "http://localhost:3000")


def send_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    notification_log_id: Optional[int] = None,
) -> bool:
    """
    Відправляє email через SMTP.
    
    Args:
        to: Email отримувача
        subject: Тема листа
        body_text: Текстова версія листа
        body_html: HTML версія листа (опціонально)
        notification_log_id: ID запису в notification_logs
        
    Returns:
        True якщо відправлено успішно, False якщо помилка
    """
    try:
        # Перевірка налаштувань SMTP
        if not SMTP_USER or not SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            logger.info(f"Would send email to {to}: {subject}")
            # У dev режимі логуємо замість відправки
            logger.debug(f"Body: {body_text[:200]}...")
            return False  # Не вважаємо помилкою - просто не налаштовано
        
        # Створення повідомлення
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to
        msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Додаємо текстову частину
        part_text = MIMEText(body_text, 'plain', 'utf-8')
        msg.attach(part_text)
        
        # Додаємо HTML частину якщо є
        if body_html:
            part_html = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(part_html)
        
        # Відправка через SMTP
        if SMTP_USE_SSL:
            # SSL з'єднання
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # TLS з'єднання (default)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {to}: {subject}")
        if notification_log_id:
            logger.info(f"   Notification Log ID: {notification_log_id}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error sending email to {to}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending email to {to}: {e}")
        return False


def send_bulk_email(
    recipients: list[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> dict:
    """
    Відправляє email кільком отримувачам.
    
    Args:
        recipients: Список email адрес
        subject: Тема листа
        body_text: Текстова версія
        body_html: HTML версія
        
    Returns:
        Dictionary {"sent": count, "failed": count}
    """
    sent_count = 0
    failed_count = 0
    
    for recipient in recipients:
        success = send_email(
            to=recipient,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Bulk email completed: {sent_count} sent, {failed_count} failed")
    return {"sent": sent_count, "failed": failed_count}


def render_template(template_name: str, context: dict) -> tuple[str, str]:
    """
    Рендерить email template (text та HTML версії).
    
    Args:
        template_name: Назва шаблону (наприклад, "new_case")
        context: Дані для підстановки в шаблон
        
    Returns:
        Tuple (text_body, html_body)
    """
    try:
        # Додаємо загальні змінні до контексту
        context['current_year'] = datetime.now().year
        context['crm_url'] = CRM_URL
        
        # Завантажуємо HTML шаблон
        template_file = f"{template_name}.html"
        template = jinja_env.get_template(template_file)
        html_body = template.render(**context)
        
        # Генеруємо текстову версію
        text_body = _generate_text_version(template_name, context)
        
        return text_body, html_body
        
    except Exception as e:
        logger.error(f"Error rendering template {template_name}: {e}")
        # Fallback на простий текст
        text = f"Повідомлення від Ohmatdyt CRM\n\n{context.get('message', 'Деталі в системі CRM')}"
        html = f"<p>{text}</p>"
        return text, html


def _generate_text_version(template_name: str, context: dict) -> str:
    """
    Генерує текстову версію email на основі типу шаблону.
    
    Args:
        template_name: Назва шаблону
        context: Дані для підстановки
        
    Returns:
        Текстова версія листа
    """
    # Базовий текст залежно від типу
    text_templates = {
        "new_case": """
🏥 Ohmatdyt CRM - Нове звернення

Вітаємо, {executor_name}!

Вам призначено нове звернення для обробки.

Номер звернення: #{case_public_id}
Категорія: {category_name}
Канал: {channel_name}
Дата створення: {created_at}

ЗАЯВНИК:
Ім'я: {applicant_name}
{phone_line}
{email_line}

СУТЬ ЗВЕРНЕННЯ:
{description}

Посилання: {crm_url}/cases/{case_public_id}

---
Будь ласка, візьміть звернення в роботу якомога швидше.

© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",
        
        "case_taken": """
🏥 Ohmatdyt CRM - Звернення взято в роботу

Звернення #{case_public_id} взято в роботу виконавцем.

Номер звернення: #{case_public_id}
Виконавець: {executor_name}
Email виконавця: {executor_email}
Статус: В роботі
Дата взяття: {taken_at}

ДЕТАЛІ:
Категорія: {category_name}
Заявник: {applicant_name}

Посилання: {crm_url}/cases/{case_public_id}

---
© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",
        
        "status_changed": """
🏥 Ohmatdyt CRM - Статус змінено

Статус звернення #{case_public_id} було змінено.

Номер звернення: #{case_public_id}
Попередній статус: {old_status_display}
Новий статус: {new_status_display}
Дата зміни: {changed_at}
Виконавець: {executor_name}

{comment_section}

ДЕТАЛІ:
Категорія: {category_name}
Заявник: {applicant_name}

Посилання: {crm_url}/cases/{case_public_id}

---
© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",
        
        "new_comment": """
🏥 Ohmatdyt CRM - Новий коментар

До звернення #{case_public_id} додано новий коментар.

Номер звернення: #{case_public_id}
Автор: {author_name}
Роль: {author_role}
Тип: {comment_type}
Дата: {created_at}

КОМЕНТАР:
{comment_text}

ДЕТАЛІ:
Категорія: {category_name}
Статус: {status_display}
Заявник: {applicant_name}

Посилання: {crm_url}/cases/{case_public_id}

---
© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",
        
        "temp_password": """
🏥 Ohmatdyt CRM - Тимчасовий пароль

Вітаємо, {username}!

Для вашого облікового запису було створено тимчасовий пароль.

Логін: {username}
Email: {email}
Роль: {role_display}

ТИМЧАСОВИЙ ПАРОЛЬ: {temp_password}

⚠️ ВАЖЛИВО:
- Цей пароль дійсний тільки для першого входу
- Після входу ви ПОВИННІ змінити пароль
- Не передавайте пароль іншим особам
- Видаліть це повідомлення після зміни паролю

ІНСТРУКЦІЯ:
1. Перейдіть: {crm_url}/login
2. Введіть логін: {username}
3. Введіть тимчасовий пароль
4. Встановіть новий пароль (мін. 8 символів)

Посилання для входу: {crm_url}/login

---
© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",

        "reassigned": """
🏥 Ohmatdyt CRM - Звернення передано

Звернення #{case_public_id} було передано іншому виконавцю.

Номер звернення: #{case_public_id}
Попередній виконавець: {old_executor_name}
Новий виконавець: {new_executor_name}
Дата передачі: {reassigned_at}

{reason_section}

ДЕТАЛІ:
Категорія: {category_name}
Статус: {status_display}
Заявник: {applicant_name}

Посилання: {crm_url}/cases/{case_public_id}

---
© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",

        "escalation": """
🏥 Ohmatdyt CRM - ЗВЕРНЕННЯ ПОТРЕБУЄ УВАГИ!

⚠️ Звернення #{case_public_id} вимагає негайної уваги!

ПРИЧИНА ЕСКАЛАЦІЇ:
{escalation_reason}

Номер звернення: #{case_public_id}
Дата створення: {created_at}
Дата ескалації: {escalated_at}
Виконавець: {executor_name}
Статус: {status_display}
{overdue_line}

ДЕТАЛІ:
Категорія: {category_name}
Заявник: {applicant_name}
{phone_line}

СУТЬ ЗВЕРНЕННЯ:
{description}

Посилання: {crm_url}/cases/{case_public_id}

---
НЕОБХІДНІ ДІЇ: Будь ласка, перегляньте звернення та вживіть заходів якомога швидше!

© {current_year} Національна дитяча спеціалізована лікарня "ОХМАТДИТ"
""",
    }
    
    # Отримуємо шаблон
    template = text_templates.get(template_name, "Повідомлення від Ohmatdyt CRM\n\n{message}")
    
    # Додаткова обробка контексту для текстової версії
    text_context = context.copy()
    
    # Обробка опціональних полів
    text_context['phone_line'] = f"Телефон: {context.get('applicant_phone', '')}" if context.get('applicant_phone') else ""
    text_context['email_line'] = f"Email: {context.get('applicant_email', '')}" if context.get('applicant_email') else ""
    text_context['comment_section'] = f"КОМЕНТАР ДО ЗМІНИ:\n{context.get('status_comment', '')}\n" if context.get('status_comment') else ""
    text_context['reason_section'] = f"ПРИЧИНА ПЕРЕДАЧІ:\n{context.get('reassignment_reason', '')}\n" if context.get('reassignment_reason') else ""
    text_context['overdue_line'] = f"⏱️ Прострочено на {context.get('days_overdue', 0)} днів" if context.get('days_overdue', 0) > 0 else ""
    text_context['comment_type'] = "🔒 Внутрішній" if context.get('is_internal') else "👁️ Публічний"
    
    try:
        return template.format(**text_context).strip()
    except KeyError as e:
        logger.error(f"Missing variable in text template: {e}")
        return f"Повідомлення від Ohmatdyt CRM\n\nДеталі в системі: {CRM_URL}"
