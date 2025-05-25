import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import styles from './MessageItem.module.css';

const MessageItem = ({ message }) => {
  const { content, sender, timestamp, files, isError } = message;
  
  // タイムスタンプをフォーマット
  const formattedTime = new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(timestamp));

  // マークダウンコンポーネントのカスタマイズ
  const markdownComponents = {
    // コードブロックのスタイリング
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <pre className={styles.codeBlock}>
          <code className={className} {...props}>
            {children}
          </code>
        </pre>
      ) : (
        <code className={styles.inlineCode} {...props}>
          {children}
        </code>
      );
    },
    // リンクのスタイリング
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className={styles.link}>
        {children}
      </a>
    ),
    // テーブルのスタイリング
    table: ({ children }) => (
      <div className={styles.tableWrapper}>
        <table className={styles.table}>{children}</table>
      </div>
    ),
    // 引用のスタイリング
    blockquote: ({ children }) => (
      <blockquote className={styles.blockquote}>{children}</blockquote>
    ),
  };

  // メッセージ内容をレンダリング
  const renderContent = () => {
    if (sender === 'ai') {
      return (
        <div className={styles.messageText}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={markdownComponents}
          >
            {content}
          </ReactMarkdown>
        </div>
      );
    } else {
      // ユーザーメッセージは簡単なマークダウンのみ対応
      return (
        <div className={styles.messageText}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {content}
          </ReactMarkdown>
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

export default MessageItem;