import React from 'react';
import styles from './MessageItem.module.css';

const MessageItem = ({ message }) => {
  const { content, sender, timestamp, files, isError } = message;
  
  // タイムスタンプをフォーマット
  const formattedTime = new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(timestamp));

  // AIメッセージをドキュメント形式で表示する処理
  const renderContent = () => {
    if (sender === 'ai') {
      return formatDocumentStyle(content);
    } else {
      return (
        <div className={styles.messageText}>
          {formatMessage(content)}
        </div>
      );
    }
  };

  return (
    <div className={`${styles.messageItem} ${styles[sender]} ${isError ? styles.error : ''}`}>
      <div className={styles.messageContent}>
        {/* 添付ファイルがある場合は表示 */}
        {files && files.length > 0 && (
          <div className={styles.fileAttachments}>
            {files.map((file, index) => (
              <div key={index} className={styles.fileItem}>
                <span className={styles.fileName}>{file.name}</span>
                <span className={styles.fileSize}>({formatFileSize(file.size)})</span>
              </div>
            ))}
          </div>
        )}
        
        {/* メッセージ本文 */}
        {renderContent()}
      </div>
      
      <div className={styles.messageTime}>{formattedTime}</div>
    </div>
  );
};

// ファイルサイズをフォーマット
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

// 通常のメッセージをフォーマット（改行やコードブロックなど）
const formatMessage = (text) => {
  if (!text) return '';

  // 行ごとに処理
  const lines = text.split('\n');
  
  return lines.map((line, i) => (
    <p key={i}>{line || '\u00A0'}</p>
  ));
};

// AIメッセージをドキュメントスタイルでフォーマット
const formatDocumentStyle = (text) => {
  if (!text) return '';

  // 行ごとに処理
  const lines = text.split('\n');
  
  return (
    <div className={styles.messageText}>
      {lines.map((line, i) => (
        <p key={i}>{line || '\u00A0'}</p>
      ))}
    </div>
  );
};

export default MessageItem;