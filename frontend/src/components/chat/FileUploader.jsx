import React, { useState, useRef } from 'react';
import styles from './FileUploader.module.css';

const FileUploader = ({ onFilesSelected }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    
    setSelectedFiles(prev => [...prev, ...files]);
    onFilesSelected([...selectedFiles, ...files]);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className={styles.container}>
      <input
        type="file"
        multiple
        onChange={handleFileChange}
        className={styles.fileInput}
        ref={fileInputRef}
      />
      
      <button 
        type="button" 
        className={styles.uploadButton}
        onClick={handleClick}
      >
        <span>ファイル添付</span>
      </button>
    </div>
  );
};

export default FileUploader;