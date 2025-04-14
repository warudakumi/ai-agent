import React, { useState } from 'react';
import FileUploader from './FileUploader';
import styles from './InputArea.module.css';

const InputArea = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState([]);

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

  return (
    <div className={styles.inputAreaContainer}>
      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <FileUploader onFilesSelected={handleFilesSelected} />
        
        <div className={styles.textareaWrapper}>
          <textarea
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
      </form>
    </div>
  );
};

export default InputArea;