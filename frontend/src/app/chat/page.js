'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import ChatArea from '@/components/chat/ChatArea';
import styles from './page.module.css';

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  
  return (
    <div className={styles.container}>
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <div className={styles.content}>
        <main className={styles.main}>
          <ChatArea />
        </main>
      </div>
    </div>
  );
}