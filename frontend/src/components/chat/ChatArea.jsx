'use client';

import React, { useState, useRef, useEffect, useContext } from 'react';
import MessageItem from './MessageItem';
import InputArea from './InputArea';
import apiService from '@/services/api';
import { useSettings } from '@/context/SettingsContext';
import styles from './ChatArea.module.css';

// サイドバーの状態を親コンポーネントから受け取る
const ChatArea = ({ isSidebarOpen, onClearMessages }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { sessionId } = useSettings(); // SettingsContextからセッションIDを取得
  const messagesEndRef = useRef(null);

  // 会話履歴をクリアする関数
  const clearMessages = async () => {
    try {
      // フロントエンドの表示をクリア
      setMessages([]);
      
      // バックエンドの会話履歴もクリア（LLM設定は保持）
      if (sessionId) {
        await apiService.chat.clearHistory(sessionId);
        console.log('会話履歴をクリアしました（LLM設定は保持）');
      }
    } catch (error) {
      console.error('会話履歴クリアエラー:', error);
      // エラーが発生してもフロントエンドの表示はクリアされている
    }
  };

  // 親コンポーネントからクリア関数を呼び出せるようにする
  useEffect(() => {
    if (onClearMessages) {
      onClearMessages(clearMessages);
    }
  }, [onClearMessages]);

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
      
      // APIにメッセージを送信（セッションIDを使用）
      const response = await apiService.chat.sendMessage(text, sessionId, files);
      
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
        content: 'エラーが発生しました。LLM設定を確認してください。',
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

  const hasMessages = messages.length > 0;

  return (
    <>
      <div className={styles.chatContainer}>
        <div className={styles.messageList}>
          {!hasMessages ? (
            <div className={styles.emptyState}>
              <h2>AIエージェント</h2>
              <p>質問や指示を入力して、会話を始めましょう。</p>
              <div className={styles.centeredInputArea}>
                <InputArea 
                  onSendMessage={handleSendMessage} 
                  disabled={isLoading} 
                  centered={true}
                  isSidebarOpen={isSidebarOpen}
                />
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageItem key={msg.id} message={msg} />
              ))}
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
            </>
          )}
        </div>
        
        {/* メッセージリスト内の入力欄は非表示 */}
        <div className={styles.inputAreaWrapper}>
          <InputArea 
            onSendMessage={handleSendMessage} 
            disabled={isLoading} 
            centered={false}
            isSidebarOpen={isSidebarOpen}
          />
        </div>
      </div>
      
      {/* 画面下部に固定表示される入力欄 */}
      {hasMessages && (
        <InputArea 
          onSendMessage={handleSendMessage} 
          disabled={isLoading} 
          centered={false}
          isSidebarOpen={isSidebarOpen}
        />
      )}
    </>
  );
};

export default ChatArea;