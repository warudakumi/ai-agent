'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import LLMSettings from '@/components/settings/LLMSettings';
import MSGraphSettings from '@/components/settings/MSGraphSettings';
import styles from './page.module.css';

export default function SettingsPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  
  return (
    <div className={`${styles.container} ${isSidebarOpen ? styles.sidebarOpen : ''}`}>
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <div className={styles.content}>
        <main className={styles.main}>
          <div className={styles.settingsContainer}>
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>LLM設定</h2>
              <p className={styles.sectionDescription}>
                AIモデルの接続設定を行います。Azure OpenAIまたはローカルLLMを選択できます。
              </p>
              <LLMSettings />
            </div>
            
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>Microsoft Graph設定</h2>
              <p className={styles.sectionDescription}>
                Microsoft 365連携のための設定です。将来的なOffice 365機能のために使用されます。
              </p>
              <MSGraphSettings />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}