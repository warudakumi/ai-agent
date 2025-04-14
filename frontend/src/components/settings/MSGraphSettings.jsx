'use client';

import React, { useState, useEffect } from 'react';
import { useSettings } from '@/context/SettingsContext';
import styles from './MSGraphSettings.module.css';

const MSGraphSettings = () => {
  const { settings, updateMSGraphSettings } = useSettings();
  const [formValues, setFormValues] = useState({
    client_id: '',
    tenant_id: '',
    client_secret: '',
    redirect_uri: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState(null);

  // 初期値をセット
  useEffect(() => {
    if (settings?.msgraph) {
      setFormValues({
        client_id: settings.msgraph.client_id || '',
        tenant_id: settings.msgraph.tenant_id || '',
        client_secret: settings.msgraph.client_secret || '',
        redirect_uri: settings.msgraph.redirect_uri || '',
      });
    }
  }, [settings]);

  // 入力変更ハンドラ
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormValues(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // フォーム送信ハンドラ
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setSaveMessage(null);
      
      const success = await updateMSGraphSettings(formValues);
      
      if (success) {
        setSaveMessage({ type: 'success', text: '設定を保存しました' });
      } else {
        setSaveMessage({ type: 'error', text: '設定の保存に失敗しました' });
      }
    } catch (error) {
      console.error('設定保存エラー:', error);
      setSaveMessage({ type: 'error', text: 'エラー: ' + error.message });
    } finally {
      setIsSaving(false);
      
      // 3秒後にメッセージを消す
      setTimeout(() => {
        setSaveMessage(null);
      }, 3000);
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <p className={styles.description}>
          Microsoft Graph APIに接続するための設定です。Office 365機能を使用する場合に設定してください。
          （現時点では使用しません）
        </p>
        
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="client_id">
            アプリケーション（クライアント）ID
          </label>
          <input
            type="text"
            id="client_id"
            name="client_id"
            value={formValues.client_id}
            onChange={handleChange}
            className={styles.input}
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
        </div>
        
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="tenant_id">
            ディレクトリ（テナント）ID
          </label>
          <input
            type="text"
            id="tenant_id"
            name="tenant_id"
            value={formValues.tenant_id}
            onChange={handleChange}
            className={styles.input}
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
        </div>
        
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="client_secret">
            クライアントシークレット
          </label>
          <input
            type="password"
            id="client_secret"
            name="client_secret"
            value={formValues.client_secret}
            onChange={handleChange}
            className={styles.input}
            placeholder="your-client-secret"
          />
        </div>
        
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="redirect_uri">
            リダイレクトURI
          </label>
          <input
            type="text"
            id="redirect_uri"
            name="redirect_uri"
            value={formValues.redirect_uri}
            onChange={handleChange}
            className={styles.input}
            placeholder="https://your-app.com/auth/callback"
          />
        </div>
        
        <div className={styles.formActions}>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={isSaving}
          >
            {isSaving ? '保存中...' : '設定を保存'}
          </button>
          
          {saveMessage && (
            <div className={`${styles.saveMessage} ${styles[saveMessage.type]}`}>
              {saveMessage.text}
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default MSGraphSettings;