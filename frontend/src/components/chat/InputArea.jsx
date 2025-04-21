import React, { useState, useRef, useEffect } from 'react';
import FileUploader from './FileUploader';
import styles from './InputArea.module.css';

const InputArea = ({ onSendMessage, disabled, centered = false, isSidebarOpen = false }) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState([]);
  const textareaRef = useRef(null);
  
  // テキストエリアの高さを自動調整する関数
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // 初期高さにリセット
    textarea.style.height = 'auto';
    
    // スクロールの高さに合わせて調整（最大高さは200px）
    const newHeight = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${newHeight}px`;
  };
  
  // メッセージが変更されたときに高さを調整
  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if ((!message.trim() && files.length === 0) || disabled) return;
    
    onSendMessage(message, files);
    setMessage('');
    setFiles([]);
  };

  const handleKeyDown = (e) => {
    // Ctrl+Enterで送信
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit(e);
    }
  };

  const handleFilesSelected = (selectedFiles) => {
    setFiles(selectedFiles);
  };
  
  const removeFile = (index) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  };

  return (
    <div className={`${styles.inputAreaContainer} ${centered ? styles.centered : ''} ${isSidebarOpen ? styles.sidebarOpen : ''}`}>
      <form onSubmit={handleSubmit} className={styles.inputForm}>
        {/* ファイルアップローダーを上部に配置 */}
        <div className={styles.uploaderContainer}>
          <FileUploader onFilesSelected={handleFilesSelected} />
        </div>
        
        {/* ファイルリスト表示エリア */}
        {files.length > 0 && (
          <div className={styles.fileListContainer}>
            {files.map((file, idx) => (
              <div key={idx} className={styles.fileItem}>
                <span className={styles.fileName}>{file.name}</span>
                <button 
                  type="button"
                  className={styles.removeButton}
                  onClick={() => removeFile(idx)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        
        <div className={styles.inputContainer}>
          <div className={styles.textareaWrapper}>
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="メッセージを入力（Ctrl+Enterで送信）..."
              className={styles.textarea}
              disabled={disabled}
            />
          </div>
          
          <button 
            type="submit" 
            className={styles.sendButton}
            disabled={disabled || (!message.trim() && files.length === 0)}
          >
            送信
          </button>
        </div>
      </form>
    </div>
  );
};

export default InputArea;