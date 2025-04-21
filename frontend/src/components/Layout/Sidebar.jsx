'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

const Sidebar = ({ isOpen = true, onToggle }) => {
  const pathname = usePathname();
  
  // ナビゲーション項目
  const navItems = [
    { path: '/chat', label: 'チャット' },
    { path: '/settings', label: '設定' },
  ];
  
  return (
    <>
      <div className={`${styles.sidebar} ${isOpen ? styles.open : styles.closed}`}>
        <div className={styles.logoContainer}>
          <Link href="/">
            <img src="/images/logo.png" alt="Agent Logo" height="40" />
          </Link>
        </div>
        
        <nav className={styles.nav}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              href={item.path}
              className={`${styles.navItem} ${pathname === item.path ? styles.active : ''}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        
        <div className={styles.footer}>
          <p className={styles.copyright}>© 2025 copyright placeholder</p>
        </div>
      </div>
      
      <button 
        className={`${styles.toggleButton} ${isOpen ? styles.open : styles.closed}`}
        onClick={onToggle}
        aria-label={isOpen ? 'サイドバーを閉じる' : 'サイドバーを開く'}
      >
        <span className={styles.toggleIcon}></span>
      </button>
    </>
  );
};

export default Sidebar;