# 🏆 Стандарты составления резюме (Best Practices Guide)

Все эталонные шаблоны в папке `templates/` составлены по международным стандартам ведущих технологических компаний (FAANG / Big Tech: Google, Meta, Amazon) и оптимизированы для автоматизированных систем скрининга (ATS — Applicant Tracking Systems).

---

## 1. Формула достижений Google (XYZ Formula)

Главная ошибка 90% резюме — перечисление обязанностей вместо результатов (*«Занимался настройкой Kubernetes»*, *«Писал микросервисы»*).

В наших шаблонах каждый буллет опыта строится строго по формуле:
> **«Достиг [X], что измерено метрикой [Y], применив решение/технологию [Z]»**  
> *(Accomplished [X] as measured by [Y], by doing [Z])*

### Примеры:
- ❌ *Плохо:* «Оптимизировал базу данных PostgreSQL».
- ✔️ *Best Practice:* «Оптимизировал схему и индексы в PostgreSQL (размер кластера > 4 TB), **сократив p95 latency тяжелых аналитических запросов с 1.8 с до 120 мс**».
- ❌ *Плохо:* «Настроил CI/CD пайплайны в GitLab».
- ✔️ *Best Practice:* «Автоматизировал CI/CD пайплайны на базе GitLab CI и ArgoCD, **сократив time-to-market новых релизов с 10 дней до 4 часов**».
- ❌ *Плохо:* «Экономил деньги на облаке».
- ✔️ *Best Practice:* «Реализовал аудит облачных мощностей AWS FinOps и миграцию на spot-инстансы, **снизив ежемесячный счет за облако на $18,000 (32%) без потери SLA**».

---

## 2. Структура резюме по международному стандарту

1. **Заголовок (Header):**
   - Имя Фамилия (крупно).
   - Точное профессиональное позиционирование (Target Title).
   - Контакты (Email, Telegram/Телефон, Локация/Формат: Remote / Relocation, ссылки на LinkedIn и GitHub).
2. **Профессиональное резюме (Executive Summary):**
   - 3–4 емких предложения.
   - Никаких клише (*«стрессоустойчивый, быстро обучаемый»*).
   - Только: общий стаж (X+ лет), специализация, масштаб систем (RPS, DAU, бюджеты), ключевой стек и главные бизнес-результаты.
3. **Карта компетенций (Core Competencies & Tech Stack):**
   - Логически сгруппированный стек (Языки, Архитектура, Базы данных, Cloud/DevOps, Безопасность).
   - Это гарантирует 100% прохождение ATS-фильтров по ключевым словам.
4. **Профессиональный опыт (Professional Experience):**
   - В обратном хронологическом порядке (текущее место сверху).
   - Компания, должность, даты, формат работы.
   - 3–5 буллетов с сильными глаголами действия (Спроектировал, Реализовал, Автоматизировал, Оптимизировал, Сократил).
5. **Сертификаты и образование (Certifications & Education):**
   - Международно признанные сертификаты вендоров (AWS, Kubernetes/CKA, Terraform, PMP, CISSP) с указанием года получения.
   - Высшее образование (ВУЗ, специальность, степень).

---

## 3. Каталог эталонных бенчмарк-шаблонов

В репозитории доступны готовые профили:
* [`cv_software_engineer.md`](cv_software_engineer.md) — Senior Full-Stack / Backend Engineer (Python, Go, K8s, Highload).
* [`cv_devops_sysadmin.md`](cv_devops_sysadmin.md) — Lead DevOps & Cloud Infrastructure Architect (K8s, Terraform, AWS, FinOps).
* [`cv_ml_ai_engineer.md`](cv_ml_ai_engineer.md) — Senior ML & GenAI Engineer (LLMs, vLLM, RAG, PyTorch, 40k+ RPS).
* [`cv_security_engineer.md`](cv_security_engineer.md) — Lead Security Engineer / DevSecOps (PCI-DSS, SOC2, Cloud Security, K8s Hardening).
* [`cv_project_manager.md`](cv_project_manager.md) — Senior Technical PM / Delivery Manager (Agile, PMP, Budgets $3M, GenAI Delivery).
* [`skills_matrix_template.md`](skills_matrix_template.md) — Канонический мастер-профиль кандидата (Единый источник истины).
