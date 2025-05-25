'use client';

import React, { useState, useRef } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import ChatArea from '@/components/chat/ChatArea';
import styles from './page.module.css';

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const clearMessagesRef = useRef(null);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleClearMessages = (clearFunction) => {
    clearMessagesRef.current = clearFunction;
  };

  const clearChatHistory = () => {
    if (clearMessagesRef.current) {
      clearMessagesRef.current();
    }
  };
  
  return (
    <div className={`${styles.container} ${isSidebarOpen ? styles.sidebarOpen : ''}`}>
      <Sidebar 
        isOpen={isSidebarOpen} 
        onToggle={toggleSidebar} 
        onClearChat={clearChatHistory}
      />
      <div className={styles.content}>
        <main className={styles.main}>
          <ChatArea 
            isSidebarOpen={isSidebarOpen} 
            onClearMessages={handleClearMessages}
          />
        </main>
      </div>
    </div>
  );
}