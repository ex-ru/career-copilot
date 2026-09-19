# Артем Кузнецов
**Senior Machine Learning & GenAI Engineer**  
📧 artem.kuznetsov.ai@example.com | 📱 +357 99 876543 | 📍 Limassol / Remote | 🌐 linkedin.com/in/artem-kuznetsov-ai | 💻 github.com/artem-ai

---

## Профессиональное резюме (Summary)
Senior ML & GenAI Engineer с 6+ годами практического опыта разработки, оптимизации и вывода в продакшн высоконагруженных моделей машинного обучения и LLM-пайплайнов. Глубокая экспертиза в дообучении открытых моделей (Llama, Qwen, Mistral: LoRA, QLoRA, DPO), RAG-архитектурах, инференс-оптимизации (vLLM, TensorRT-LLM, quantization) и MLOps на базе Kubernetes и GCP/AWS. Доказанный опыт сокращения latency генерации LLM на 65% и развертывания распределенных моделей, обслуживающих 40,000+ RPS с SLA 99.95%.

---

## Ключевые компетенции и стек (Tech Stack)
- **ML & Deep Learning:** Python, PyTorch, Hugging Face (Transformers, PEFT, TRL), DeepSpeed, LangChain, LlamaIndex
- **GenAI & LLMOps:** Fine-tuning (LoRA/QLoRA/DPO), Prompt Engineering, RAG, vLLM, Triton Inference Server, TensorRT-LLM
- **Векторные базы данных & Кэши:** Qdrant, Milvus, ChromaDB, Redis Semantic Cache, PostgreSQL (pgvector)
- **Инженерия & Данные:** FastEmbed, Ray, Apache Spark, Kafka, Docker, Kubernetes (KServe, Ray on K8s), MLflow, Weights & Biases
- **Качество & Мониторинг:** RAGAS, DeepEval, Prometheus, Grafana, Evidently AI (Data/Concept Drift)

---

## Профессиональный опыт (Experience)

### NeuroCore Labs — Senior GenAI / LLM Systems Engineer
*Июнь 2022 — Настоящее время | Удаленно / Кипр*
- Спроектировал и развернул отказоустойчивую платформу инференса LLM на базе vLLM и Triton в Kubernetes (GKE), обрабатывающую 35,000 RPS для 12 млн активных пользователей.
- Сократил Time-to-First-Token (TTFT) с 850 мс до 180 мс и увеличил пропускную способность токенов в 3.2 раза за счет применения PagedAttention, квантования FP8/AWQ и спекулятивного декодинга.
- Реализовал гибридную RAG-систему (Dense + Sparse retrieval + Re-ranking на базе Qdrant и BGE-Reranker) для анализа юридических и финансовых документов, повысив точность ответов (RAGAS faithfulness score) с 71% до 94%.
- Внедрил автоматический пайплайн DPO-дообучения (Direct Preference Optimization) на пользовательских фидбеках, сократив процент галлюцинаций модели на 40%.

### DataPulse Analytics — Machine Learning Engineer
*Сентябрь 2019 — Май 2022 | Москва / Гибрид*
- Разработал и вывел в production рекомендательную систему для маркетплейса с 5M SKU на базе двухбашенных нейросетей (Two-Tower DSSM), увеличив CTR персонализированных рекомендаций на 24% и GMV на 14%.
- Оптимизировал пайплайн предобработки терабайтных табличных и текстовых данных с использованием Apache Spark и Ray, ускорив цикл обучения моделей с 36 часов до 4.5 часов.
- Настроил CI/CD для ML-моделей (GitLab CI + MLflow + Docker), сократив время от проверки гипотезы до деплоя новой модели с 3 недель до 2 дней.

---

## Сертификаты и образование
- **DeepLearning.AI**: Generative AI with Large Language Models (2023)
- **Google Cloud Certified**: Professional Machine Learning Engineer (2022)
- **Московский Физико-Технический Институт (МФТИ)**, Прикладная математика и информатика, Магистр (2019)
