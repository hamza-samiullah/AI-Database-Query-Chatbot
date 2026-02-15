import React from 'react';
import clsx from 'clsx';
import { User, Bot } from 'lucide-react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={clsx(
            "flex w-full mt-2 space-x-3 max-w-4xl mx-auto",
            isUser ? "justify-end" : "justify-start"
        )}>
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot size={20} className="text-blue-600" />
                </div>
            )}

            <div className={clsx(
                "relative px-4 py-2 rounded-lg text-sm shadow-sm",
                isUser ? "bg-blue-600 text-white rounded-br-none" : "bg-white text-gray-800 rounded-bl-none border border-gray-200"
            )}>
                <p className="whitespace-pre-wrap">{message.content}</p>


            </div>

            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <User size={20} className="text-gray-600" />
                </div>
            )}
        </div>
    );
};

export default MessageBubble;
