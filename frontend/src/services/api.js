import axios from 'axios';

// デフォルトの設定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// axios インスタンスの作成
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// APIリクエスト関数
const apiService = {
  // チャット関連
  chat: {
    // メッセージを送信する
    sendMessage: async (message, files = [], sessionId = null) => {
      const formData = new FormData();
      formData.append('message', message);
      
      if (sessionId) {
        formData.append('session_id', sessionId);
      }
      
      // ファイルが存在する場合はフォームデータに追加
      if (files && files.length > 0) {
        files.forEach(file => {
          formData.append('files', file);
        });
      }
      
      try {
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
    // LLM設定を保存する
    saveLLMSettings: async (settings) => {
      try {
        const response = await api.post('/api/settings/llm', settings);
        return response.data;
      } catch (error) {
        console.error('LLM設定保存エラー:', error);
        throw error;
      }
    },
    
    // LLM設定を取得する
    getLLMSettings: async () => {
      try {
        const response = await api.get('/api/settings/llm');
        return response.data;
      } catch (error) {
        console.error('LLM設定取得エラー:', error);
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