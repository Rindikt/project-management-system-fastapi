import React, { useState } from 'react';
import { UserPlus, Loader2, CheckCircle, XCircle } from 'lucide-react';

// Константы для доступа к API
const API_KEY = ""; // Оставьте пустым, ключ будет предоставлен средой выполнения Canvas
const BASE_URL = "/api"; // Предполагаем, что API находится по относительному пути

/**
 * Вспомогательная функция для выполнения fetch с логикой экспоненциальной задержки (Backoff).
 */
async function fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (response.ok) {
                return response;
            }
            // Для не-2xx ответов (400, 403, 500) не повторяем, а сразу бросаем ошибку
            // для обработки конкретной ошибки приложением.
            throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        } catch (error) {
            if (i === maxRetries - 1) {
                console.error("Fetch failed after multiple retries:", error);
                throw error;
            }
            // Экспоненциальная задержка: 1с, 2с, 4с
            const delay = Math.pow(2, i) * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

/**
 * Компонент для отображения сообщений (успех/ошибка).
 */
const MessageDisplay = ({ type, text }) => {
    if (!text) return null;

    const icon = type === 'success' ? <CheckCircle className="w-5 h-5 mr-2 text-green-600" /> : <XCircle className="w-5 h-5 mr-2 text-red-600" />;
    const colorClass = type === 'success' ? 'bg-green-50 border-green-500 text-green-800' : 'bg-red-50 border-red-500 text-red-800';

    return (
        <div className={`p-4 border-l-4 ${colorClass} rounded-lg mb-6 flex items-start shadow-md transition-all duration-300`} role="alert">
            {icon}
            <p className="font-medium text-sm">{text}</p>
        </div>
    );
};


/**
 * Основной компонент формы добавления участника.
 * Принимает ID проекта в качестве пропса.
 */
function AddMemberForm({ projectId }) {
    // Вводимое пользователем значение (ожидаем ID, т.е. число)
    const [userIdInput, setUserIdInput] = useState('');
    const [loading, setLoading] = useState(false);
    // Сообщение для пользователя: { type: 'success' | 'error', text: '...' }
    const [message, setMessage] = useState(null);

    const handleAddMember = async (e) => {
        e.preventDefault();

        // Простая валидация и парсинг ID
        const userId = parseInt(userIdInput, 10);
        if (isNaN(userId) || userId <= 0) {
            setMessage({ type: 'error', text: 'Пожалуйста, введите корректный числовой ID пользователя.' });
            return;
        }

        setLoading(true);
        setMessage(null);

        // Формирование URL: /projects/{project_id}/members/{user_id}
        const url = `${BASE_URL}/projects/${projectId}/members/${userId}`;

        try {
            const response = await fetchWithRetry(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Предполагаем, что аутентификация обрабатывается средой/прокси
                },
            });

            // Ответ 201 Created (Успешно создано)
            if (response.status === 201) {
                const projectData = await response.json();
                const memberCount = projectData.members ? projectData.members.length : 'неизвестное';
                setMessage({
                    type: 'success',
                    text: `Участник (ID: ${userId}) успешно добавлен в проект #${projectId}. Всего участников: ${memberCount}.`
                });
                setUserIdInput(''); // Очищаем поле ввода при успехе
            } else {
                // Обработка ошибок, специфичных для бэкенда (400, 403, 500)
                const errorData = await response.json();
                const detail = errorData.detail || `Неизвестная ошибка (Статус: ${response.status})`;

                // Проверяем статус код для точного сообщения
                if (response.status === 403) {
                    setMessage({ type: 'error', text: `Ошибка доступа (403): ${detail}` });
                } else if (response.status === 400) {
                    setMessage({ type: 'error', text: `Ошибка ввода (400): ${detail}` });
                } else {
                    setMessage({ type: 'error', text: `Ошибка сервера (${response.status}): ${detail}` });
                }
            }

        } catch (error) {
            // Обработка сетевых ошибок
            setMessage({ type: 'error', text: `Сетевая ошибка: Не удалось выполнить запрос к API. ${error.message}` });
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="max-w-md mx-auto p-8 bg-white shadow-2xl rounded-2xl border border-indigo-100/50">
            <h2 className="text-2xl font-extrabold mb-6 text-gray-800 flex items-center border-b pb-4">
                <UserPlus className="w-6 h-6 mr-3 text-indigo-600" />
                Управление участниками проекта
            </h2>

            <MessageDisplay {...message} />

            <form onSubmit={handleAddMember} className="space-y-6">
                <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                    <p className="text-sm font-semibold text-indigo-700 mb-1">Текущий проект</p>
                    <p className="text-xl font-mono text-indigo-900">ID: {projectId}</p>
                </div>

                <div>
                    <label htmlFor="userId" className="block text-sm font-medium text-gray-700 mb-2">
                        ID пользователя (числовой идентификатор)
                    </label>
                    <input
                        id="userId"
                        type="number"
                        min="1"
                        value={userIdInput}
                        onChange={(e) => setUserIdInput(e.target.value)}
                        placeholder="Например, 101"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-indigo-500 focus:border-indigo-500 shadow-inner transition duration-150 ease-in-out"
                        disabled={loading}
                    />
                    <p className="mt-2 text-xs text-gray-500">
                        Введите ID пользователя, который должен быть добавлен в проект.
                    </p>
                </div>

                <button
                    type="submit"
                    disabled={loading || !userIdInput}
                    className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-offset-2 transition duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Добавляем участника...
                        </>
                    ) : (
                        <>
                            <UserPlus className="mr-2 h-5 w-5" />
                            Добавить в проект
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}

// Главный компонент-обертка
export default function App() {
    // Используем ID 12 для соответствия вашему примеру заглушки
    const mockProjectId = 12;

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4 sm:p-6 font-[Inter]">
            <AddMemberForm projectId={mockProjectId} />
        </div>
    );
}