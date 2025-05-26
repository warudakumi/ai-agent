import axios from 'axios';

// デフォルトの設定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 現在のホスト名からAPIのベースURLを動的に決定
// ローカルホストの場合はそのまま、IPアドレスの場合はそのIPアドレスを使用
function getApiBaseUrl() {
  if (typeof window !== 'undefined') {
    // ブラウザ環境の場合
    const currentHost = window.location.hostname;
    if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
      // IPアドレスなどでアクセスしている場合
      return `http://${currentHost}:8000`;
    }
  }
  // それ以外はデフォルト値を使用
  return API_BASE_URL;
}

// axios インスタンスの作成
const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// APIリクエスト関数
const apiService = {
  // チャット関連
  chat: {
    // メッセージを送信する
    sendMessage: async (message, sessionId = null, files = null) => {
      try {
        const formData = new FormData();
        formData.append('message', message);
        
        if (sessionId) {
          formData.append('session_id', sessionId);
        }
        
        if (files && files.length > 0) {
          files.forEach((file, index) => {
            formData.append(`files`, file);
          });
        }
        
        const response = await api.post('/api/chat/message', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        return response.data;
      } catch (error) {
        console.error('メッセージ送信エラー:', error);
        throw error;
      }
    },
  },
  
  // 設定関連
  settings: {
    // LLM設定を保存する（グローバル設定）
    saveLLMSettings: async (settings) => {
      try {
        const response = await api.post('/api/settings/llm', settings);
        return response.data;
      } catch (error) {
        console.error('LLM設定保存エラー:', error);
        throw error;
      }
    },
    
    // LLM設定を取得する（グローバル設定）
    getLLMSettings: async () => {
      try {
        const response = await api.get('/api/settings/llm');
        return response.data;
      } catch (error) {
        console.error('LLM設定取得エラー:', error);
        throw error;
      }
    },
    
    // セッション別LLM設定を保存する
    saveSessionLLMSettings: async (sessionId, settings) => {
      try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('settings_data', JSON.stringify(settings));
        
        const response = await api.post('/api/settings/llm/session', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        return response.data;
      } catch (error) {
        console.error('セッション別LLM設定保存エラー:', error);
        throw error;
      }
    },
    
    // セッション別LLM設定を取得する
    getSessionLLMSettings: async (sessionId) => {
      try {
        const response = await api.get(`/api/settings/llm/session/${sessionId}`);
        return response.data;
      } catch (error) {
        console.error('セッション別LLM設定取得エラー:', error);
        throw error;
      }
    },
    
    // Microsoft Graph設定を保存する
    saveMSGraphSettings: async (settings) => {
      try {
        const response = await api.post('/api/settings/msgraph', settings);
        return response.data;
      } catch (error) {
        console.error('MSGraph設定保存エラー:', error);
        throw error;
      }
    },
    
    // Microsoft Graph設定を取得する
    getMSGraphSettings: async () => {
      try {
        const response = await api.get('/api/settings/msgraph');
        return response.data;
      } catch (error) {
        console.error('MSGraph設定取得エラー:', error);
        throw error;
      }
    },
  },
};

export default apiService;