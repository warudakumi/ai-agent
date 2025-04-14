'use client';

import React from 'react';
import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';
import LLMSettings from '@/components/settings/LLMSettings';
import MSGraphSettings from '@/components/settings/MSGraphSettings';
import styles from './page.module.css';

export default function SettingsPage() {
  return (
    <div className={styles.container}>
      <Sidebar />
      <div className={styles.content}>
        <Header />
        <main className={styles.main}>
          <div className={styles.settingsContainer}>
            <h1 className={styles.pageTitle}>設定</h1>
            
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