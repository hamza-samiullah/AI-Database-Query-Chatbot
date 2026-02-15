import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Loader2, Database } from 'lucide-react';
import MessageBubble from './MessageBubble';
import DataDisplay from './DataDisplay';

const ChatInterface = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = { role: 'user', content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            // Prepare history for API
            const history = messages.map(msg => ({
                role: msg.role === 'user' ? 'user' : 'assistant',
                content: msg.content
            }));

            const response = await axios.post('/api/chat', {
                message: userMessage.content,
                history: history
            });

            const { answer, sql, data, visualization_type } = response.data;

            const botMessage = {
                role: 'assistant',
                content: answer,
                sql: sql,
                data: data,
                visualizationType: visualization_type
            };

            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error("Error fetching data:", error);
            const errorMessage = {
                role: 'assistant',
                content: "Sorry, I encountered an error processing your request."
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
                <div className="flex items-center space-x-3">
                    <div className="bg-blue-600 p-2 rounded-lg">
                        <Database className="text-white w-6 h-6" />
                    </div>
                    <h1 className="text-xl font-bold text-gray-800">Data Chatbot <span className="text-xs font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full ml-2">Light</span></h1>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400">
                        <Database className="w-16 h-16 mb-4 opacity-20" />
                        <p>Ask a question about your data to get started.</p>
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2 w-full max-w-lg">
                            {["Show me top 5 customers", "Total sales by product category", "Sales trends for 2025", "List orders from New York"].map((q, i) => (
                                <button
                                    key={i}
                                    onClick={() => setInput(q)}
                                    className="bg-white p-3 rounded-lg border border-gray-200 text-sm text-left hover:bg-gray-50 focus:outline-none transition-colors shadow-sm"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className="space-y-4">
                        <MessageBubble message={msg} />
                        {msg.data && (
                            <DataDisplay data={msg.data} visualizationType={msg.visualizationType} />
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start max-w-4xl mx-auto w-full mt-2">
                        <div className="bg-white border border-gray-200 px-4 py-3 rounded-lg rounded-bl-none shadow-sm flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                            <span className="text-sm text-gray-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your data..."
                        className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={18} />
                    </button>
                </form>
                <div className="max-w-4xl mx-auto mt-2 text-xs text-gray-400 text-center">
                    Powered by GLM-4.5 & SQLite
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
