'use client';

import React, { createContext, useState, useEffect, useContext } from 'react';
import apiService from '@/services/api';

// デフォルト設定
const defaultSettings = {
  llm: {
    provider: 'azure', // azure、openai または local
    endpoint: '',
    api_key: '',
    deployment_name: '',
    api_version: '2023-05-15',
    model_name: 'gpt-3.5-turbo', // OpenAI用モデル名
    temperature: 0.7,
  },
  msgraph: {
    client_id: '',
    tenant_id: '',
    client_secret: '',
    redirect_uri: '',
  },
};

// コンテキスト作成
export const SettingsContext = createContext();

// プロバイダーコンポーネント
export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 設定を読み込む
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        
        // ローカルストレージから設定を取得
        const savedSettings = localStorage.getItem('agent_settings');
        
        if (savedSettings) {
          setSettings(JSON.parse(savedSettings));
        } else {
          // APIから設定を取得（APIが実装されている場合）
          try {
            const llmSettings = await apiService.settings.getLLMSettings();
            const msgraphSettings = await apiService.settings.getMSGraphSettings();
            
            setSettings({
              llm: llmSettings,
              msgraph: msgraphSettings,
            });
          } catch (apiError) {
            console.warn('API設定取得失敗、デフォルト設定を使用します:', apiError);
            // APIが失敗した場合はデフォルト設定を使用
          }
        }
      } catch (err) {
        console.error('設定読み込みエラー:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  // LLM設定を更新する
  const updateLLMSettings = async (newLLMSettings) => {
    try {
      const updatedSettings = {
        ...settings,
        llm: {
          ...settings.llm,
          ...newLLMSettings,
        },
      };
      
      setSettings(updatedSettings);
      
      // ローカルストレージに保存
      localStorage.setItem('agent_settings', JSON.stringify(updatedSettings));
      
      // APIに保存（APIが実装されている場合）
      try {
        await apiService.settings.saveLLMSettings(updatedSettings.llm);
      } catch (apiError) {
        console.warn('API設定保存失敗:', apiError);
      }
      
      return true;
    } catch (err) {
      console.error('LLM設定更新エラー:', err);
      setError(err);
      return false;
    }
  };

  // MSGraph設定を更新する
  const updateMSGraphSettings = async (newMSGraphSettings) => {
    try {
      const updatedSettings = {
        ...settings,
        msgraph: {
          ...settings.msgraph,
          ...newMSGraphSettings,
        },
      };
      
      setSettings(updatedSettings);
      
      // ローカルストレージに保存
      localStorage.setItem('agent_settings', JSON.stringify(updatedSettings));
      
      // APIに保存（APIが実装されている場合）
      try {
        await apiService.settings.saveMSGraphSettings(updatedSettings.msgraph);
      } catch (apiError) {
        console.warn('API設定保存失敗:', apiError);
      }
      
      return true;
    } catch (err) {
      console.error('MSGraph設定更新エラー:', err);
      setError(err);
      return false;
    }
  };

  // コンテキスト値
  const value = {
    settings,
    loading,
    error,
    updateLLMSettings,
    updateMSGraphSettings,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

// カスタムフック
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};