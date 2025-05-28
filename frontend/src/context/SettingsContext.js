'use client';

import React, { createContext, useState, useEffect, useContext } from 'react';
import apiService from '@/services/api';

// セッションIDを生成する関数
const generateSessionId = () => {
  return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
};

// セッションIDを取得または生成する関数
const getOrCreateSessionId = () => {
  // ブラウザ環境でのみlocalStorageにアクセス
  if (typeof window === 'undefined') {
    // サーバーサイドの場合は一時的なIDを返す
    return 'session_temp_' + Math.random().toString(36).substr(2, 9);
  }
  
  let sessionId = localStorage.getItem('agent_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('agent_session_id', sessionId);
  }
  return sessionId;
};

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
    model_type: 'quantized', // ローカルLLM用モデルタイプ（normal または quantized）
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
  const [sessionId, setSessionId] = useState('');

  // ブラウザ環境でのみセッションIDを初期化
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setSessionId(getOrCreateSessionId());
    }
  }, []);

  // 設定を読み込む
  useEffect(() => {
    // セッションIDが設定されるまで待機
    if (!sessionId) return;
    
    const loadSettings = async () => {
      try {
        setLoading(true);
        
        // まずセッション別設定を取得を試行
        try {
          const sessionSettings = await apiService.settings.getSessionLLMSettings(sessionId);
          if (sessionSettings && sessionSettings.config) {
            setSettings({
              llm: sessionSettings.config,
              msgraph: defaultSettings.msgraph, // MSGraphはローカルストレージから
            });
            console.log('セッション別設定を読み込みました');
            return;
          }
        } catch (sessionError) {
          console.warn('セッション別設定の取得に失敗:', sessionError);
        }
        
        // セッション別設定が取得できない場合、ローカルストレージから設定を取得
        if (typeof window !== 'undefined') {
          const savedSettings = localStorage.getItem('agent_settings');
          
          if (savedSettings) {
            const parsedSettings = JSON.parse(savedSettings);
            setSettings(parsedSettings);
            
            // ローカルストレージの設定をセッション別設定として保存
            try {
              await apiService.settings.saveSessionLLMSettings(sessionId, parsedSettings.llm);
              console.log('ローカルストレージの設定をセッション別設定として保存しました');
            } catch (syncError) {
              console.warn('ローカルストレージの設定をセッション別設定として保存できませんでした:', syncError);
            }
          } else {
            // デフォルト設定を使用
            console.log('デフォルト設定を使用します');
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
  }, [sessionId]);

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
      
      // ローカルストレージに保存（ブラウザ環境でのみ）
      if (typeof window !== 'undefined') {
        localStorage.setItem('agent_settings', JSON.stringify(updatedSettings));
      }
      
      // セッション別設定として保存
      try {
        await apiService.settings.saveSessionLLMSettings(sessionId, updatedSettings.llm);
        console.log('セッション別LLM設定を保存しました');
      } catch (apiError) {
        console.warn('セッション別LLM設定保存失敗:', apiError);
        // フォールバック: グローバル設定は更新しない
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
      
      // ローカルストレージに保存（ブラウザ環境でのみ）
      if (typeof window !== 'undefined') {
        localStorage.setItem('agent_settings', JSON.stringify(updatedSettings));
      }
      
      // MSGraph設定はローカルのみで管理（必要に応じてAPIに保存）
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
    sessionId,
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