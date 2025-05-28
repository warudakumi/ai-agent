'use client';

import React, { useState, useEffect } from 'react';
import { useSettings } from '@/context/SettingsContext';
import styles from './LLMSettings.module.css';

const LLMSettings = () => {
  const { settings, sessionId, updateLLMSettings } = useSettings();
  const [formValues, setFormValues] = useState({
    provider: 'azure',
    endpoint: '',
    api_key: '',
    deployment_name: '',
    api_version: '2023-05-15',
    model_name: 'gpt-3.5-turbo',
    temperature: 0.7,
    model_type: 'quantized',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState(null);

  // 初期値をセット
  useEffect(() => {
    if (settings?.llm) {
      setFormValues({
        provider: settings.llm.provider || 'azure',
        endpoint: settings.llm.endpoint || '',
        api_key: settings.llm.api_key || '',
        deployment_name: settings.llm.deployment_name || '',
        api_version: settings.llm.api_version || '2023-05-15',
        model_name: settings.llm.model_name || 'gpt-3.5-turbo',
        temperature: settings.llm.temperature || 0.7,
        model_type: settings.llm.model_type || 'quantized',
      });
    }
  }, [settings]);

  // 入力変更ハンドラ
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    
    setFormValues(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  // フォーム送信ハンドラ
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setSaveMessage(null);
      
      const success = await updateLLMSettings(formValues);
      
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
      <div className={styles.sessionInfo}>
        <p className={styles.sessionId}>
          <strong>現在のセッションID:</strong> {sessionId || '読み込み中...'}
        </p>
        <p className={styles.sessionNote}>
          ※ この設定は現在のセッション専用です。他のユーザーには影響しません。
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formSection}>
          <h3 className={styles.sectionTitle}>LLMプロバイダー</h3>
          
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <input
                type="radio"
                name="provider"
                value="azure"
                checked={formValues.provider === 'azure'}
                onChange={handleChange}
                className={styles.radio}
              />
              Azure OpenAI
            </label>
            
            <label className={styles.label}>
              <input
                type="radio"
                name="provider"
                value="openai"
                checked={formValues.provider === 'openai'}
                onChange={handleChange}
                className={styles.radio}
              />
              OpenAI
            </label>
            
            <label className={styles.label}>
              <input
                type="radio"
                name="provider"
                value="local"
                checked={formValues.provider === 'local'}
                onChange={handleChange}
                className={styles.radio}
              />
              ローカルLLM
            </label>
          </div>
        </div>
        
        {formValues.provider === 'azure' ? (
          <div className={styles.formSection}>
            <h3 className={styles.sectionTitle}>Azure OpenAI設定</h3>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="endpoint">
                エンドポイント URL
              </label>
              <input
                type="text"
                id="endpoint"
                name="endpoint"
                value={formValues.endpoint}
                onChange={handleChange}
                className={styles.input}
                placeholder="https://your-resource-name.openai.azure.com/"
                required
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="api_key">
                API キー
              </label>
              <input
                type="password"
                id="api_key"
                name="api_key"
                value={formValues.api_key}
                onChange={handleChange}
                className={styles.input}
                placeholder="your-api-key"
                required
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="deployment_name">
                デプロイメント名
              </label>
              <input
                type="text"
                id="deployment_name"
                name="deployment_name"
                value={formValues.deployment_name}
                onChange={handleChange}
                className={styles.input}
                placeholder="your-deployment"
                required
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="api_version">
                API バージョン
              </label>
              <input
                type="text"
                id="api_version"
                name="api_version"
                value={formValues.api_version}
                onChange={handleChange}
                className={styles.input}
                placeholder="2023-05-15"
              />
            </div>
          </div>
        ) : formValues.provider === 'openai' ? (
          <div className={styles.formSection}>
            <h3 className={styles.sectionTitle}>OpenAI設定</h3>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="api_key">
                API キー
              </label>
              <input
                type="password"
                id="api_key"
                name="api_key"
                value={formValues.api_key}
                onChange={handleChange}
                className={styles.input}
                placeholder="your-api-key"
                required
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="model_name">
                モデル名
              </label>
              <select
                id="model_name"
                name="model_name"
                value={formValues.model_name}
                onChange={handleChange}
                className={styles.select}
                required
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-3.5-turbo-16k">GPT-3.5 Turbo 16K</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-4o">GPT-4o</option>
              </select>
            </div>
          </div>
        ) : (
          <div className={styles.formSection}>
            <h3 className={styles.sectionTitle}>ローカルLLM設定</h3>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="endpoint">
                エンドポイント URL
              </label>
              <input
                type="text"
                id="endpoint"
                name="endpoint"
                value={formValues.endpoint}
                onChange={handleChange}
                className={styles.input}
                placeholder="http://localhost:8000"
                required
              />
              <p className={styles.helpText}>
                ローカルLLMのホストとポート (例: http://localhost:8000)
              </p>
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="model_type">
                モデルタイプ
              </label>
              <select
                id="model_type"
                name="model_type"
                value={formValues.model_type}
                onChange={handleChange}
                className={styles.select}
                required
              >
                <option value="quantized">量子化モデル (推奨)</option>
                <option value="normal">通常モデル</option>
              </select>
              <p className={styles.helpText}>
                量子化モデルはメモリ使用量が少なく、高速です
              </p>
            </div>
          </div>
        )}
        
        {/* ローカルLLM以外の場合のみTemperature設定を表示 */}
        {formValues.provider !== 'local' && (
          <div className={styles.formSection}>
            <h3 className={styles.sectionTitle}>共通設定</h3>
            
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="temperature">
                Temperature: {formValues.temperature}
              </label>
              <input
                type="range"
                id="temperature"
                name="temperature"
                min="0"
                max="1"
                step="0.1"
                value={formValues.temperature}
                onChange={handleChange}
                className={styles.rangeInput}
              />
              <div className={styles.rangeLabels}>
                <span>精確 (0)</span>
                <span>創造的 (1)</span>
              </div>
            </div>
          </div>
        )}
        
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

export default LLMSettings;