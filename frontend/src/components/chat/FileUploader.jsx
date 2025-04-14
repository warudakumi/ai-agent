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

  const removeFile = (index) => {
    const newFiles = [...selectedFiles];
    newFiles.splice(index, 1);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
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
      
      {selectedFiles.length > 0 && (
        <div className={styles.fileList}>
          {selectedFiles.map((file, idx) => (
            <div key={idx} className={styles.fileItem}>
              <span className={styles.fileName}>{file.name}</span>
              <button 
                className={styles.removeButton}
                onClick={() => removeFile(idx)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUploader;