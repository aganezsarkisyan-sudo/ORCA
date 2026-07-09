#!/bin/bash
set -e

echo "🚀 ORCA - Установка и запуск приложения"
echo "======================================="

# Проверка Python
echo "✓ Проверка Python..."
python_cmd=$(command -v python3 || command -v python)
if [ -z "$python_cmd" ]; then
    echo "❌ Python не найден! Пожалуйста, установите Python 3.11+"
    exit 1
fi

python_version=$($python_cmd --version 2>&1 | awk '{print $2}')
echo "  Найден Python: $python_version"

# Создание виртуального окружения
echo ""
echo "✓ Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    $python_cmd -m venv venv
    echo "  Виртуальное окружение создано"
else
    echo "  Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
echo ""
echo "✓ Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo ""
echo "✓ Обновление pip..."
pip install --upgrade pip --quiet

# Установка зависимостей
echo ""
echo "✓ Установка зависимостей (это займёт некоторое время)..."
pip install -r requirements.txt --quiet

# Запуск приложения
echo ""
echo "✓ Запуск ORCA..."
python main.py
