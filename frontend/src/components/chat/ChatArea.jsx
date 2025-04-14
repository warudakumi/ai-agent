'use client';

import React, { useState, useRef, useEffect } from 'react';
import MessageItem from './MessageItem';
import InputArea from './InputArea';
import apiService from '@/services/api';
import styles from './ChatArea.module.css';

const ChatArea = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  // メッセージ送信処理
  const handleSendMessage = async (text, files) => {
    if (!text.trim() && (!files || files.length === 0)) return;

    try {
      // ユーザーメッセージを表示
      const userMessage = {
        id: Date.now().toString(),
        content: text,
        sender: 'user',
        timestamp: new Date(),
        files: files ? files.map(f => ({ name: f.name, size: f.size })) : [],
      };
      
      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);
      
      // APIにメッセージを送信
      const response = await apiService.chat.sendMessage(text, files, sessionId);
      
      // セッションIDを保存
      if (response.session_id) {
        setSessionId(response.session_id);
      }
      
      // AIの応答を表示
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        content: response.message,
        sender: 'ai',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('メッセージ送信エラー:', error);
      
      // エラーメッセージを表示
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: 'エラーが発生しました。もう一度お試しください。',
        sender: 'system',
        timestamp: new Date(),
        isError: true,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messageList}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <h2>AIエージェント</h2>
            <p>質問や指示を入力して、会話を始めましょう。</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))
        )}
        {isLoading && (
          <div className={styles.thinking}>
            <div className={styles.dots}>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p>AIが考え中...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <InputArea onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatArea;